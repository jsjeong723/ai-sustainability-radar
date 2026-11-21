from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import Observation, CollectionRun

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
EIA_URL = "https://api.eia.gov/v2/electricity/retail-sales/data/"

# BLS series are intentionally broad, nationally representative indicators.
BLS_SERIES = {
    "CES0000000001": ("Total nonfarm employment", "thousand persons", "EMPLOYMENT_TOTAL"),
    "LNS14000000": ("Unemployment rate", "percent", "UNEMPLOYMENT_RATE"),
    "CES0500000003": ("Average hourly earnings, total private", "US dollars per hour", "HOURLY_EARNINGS"),
}

async def collect_bls(db: Session) -> dict:
    run = CollectionRun(source="BLS", status="running")
    db.add(run); db.commit(); db.refresh(run)
    try:
        end_year = datetime.now(timezone.utc).year
        start_year = end_year - max(1, min(settings.bls_years_back, 3)) + 1
        payload = {
            "seriesid": list(BLS_SERIES.keys()),
            "startyear": str(start_year),
            "endyear": str(end_year),
        }
        if settings.bls_api_key:
            payload["registrationkey"] = settings.bls_api_key
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(BLS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
        if data.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS API status: {data.get('status')} {data.get('message')}")
        received = inserted = 0
        for series in data.get("Results", {}).get("series", []):
            sid = series["seriesID"]
            metric, unit, indicator = BLS_SERIES[sid]
            for item in series.get("data", []):
                period_code = item.get("period", "")
                if not period_code.startswith("M") or period_code == "M13":
                    continue
                
                raw_value = item.get("value")
                
                # BLS 결측값은 0으로 처리하지 않고 건너뜀
                if raw_value is None or str(raw_value).strip() in ("", "-", "—"):
                    continue
                
                try:
                    value = float(str(raw_value).replace(",", ""))
                except (ValueError, TypeError):
                    continue
                
                received += 1
                period = f"{item['year']}-{period_code[1:]}"                
                
                # received += 1
                # period = f"{item['year']}-{period_code[1:]}"
                # value = float(item["value"])
                
                existing = db.scalar(select(Observation).where(
                    Observation.source == "BLS",
                    Observation.series_id == sid,
                    Observation.period == period
                ))
                if existing:
                    # BLS can revise historical observations; update value and footnote.
                    existing.value = value
                    existing.footnote = "; ".join(
                        f.get("text", "") for f in item.get("footnotes", []) if f.get("text")
                    ) or None
                else:
                    db.add(Observation(
                        source="BLS", indicator_code=indicator, series_id=sid,
                        metric_name=metric, period=period, value=value, unit=unit,
                        geography="United States",
                        source_url=f"https://data.bls.gov/timeseries/{sid}",
                        footnote="; ".join(f.get("text", "") for f in item.get("footnotes", []) if f.get("text")) or None
                    ))
                    inserted += 1
        run.status = "success"; run.records_received = received; run.records_inserted = inserted
        run.finished_at = datetime.now(timezone.utc); run.message = f"Years {start_year}-{end_year}"
        db.commit()
        return {"source":"BLS","status":"success","received":received,"inserted":inserted}
    except Exception as exc:
        db.rollback()
        run.status = "failed"; run.message = str(exc); run.finished_at = datetime.now(timezone.utc)
        db.add(run); db.commit()
        raise

async def collect_eia(db: Session) -> dict:
    run = CollectionRun(source="EIA", status="running")
    db.add(run); db.commit(); db.refresh(run)
    try:
        if not settings.eia_api_key:
            raise RuntimeError("EIA_API_KEY is missing. Obtain a free key from https://www.eia.gov/opendata/register.php")
        end = datetime.now(timezone.utc).date().replace(day=1)
        start = end - relativedelta(months=max(1, min(settings.eia_months_back, 60)))
        params = [
            ("api_key", settings.eia_api_key),
            ("frequency", "monthly"),
            ("data[0]", "sales"),
            ("facets[stateid][]", "US"),
            ("facets[sectorid][]", "ALL"),
            ("start", (start - relativedelta(days=1)).isoformat()),
            ("end", end.isoformat()),
            ("sort[0][column]", "period"),
            ("sort[0][direction]", "asc"),
            ("length", "5000"),
        ]
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(EIA_URL, params=params)
            response.raise_for_status()
            data = response.json()
        rows = data.get("response", {}).get("data", [])
        if not isinstance(rows, list):
            raise RuntimeError(f"Unexpected EIA response: {str(data)[:500]}")
        received = inserted = 0
        for item in rows:
            raw_value = item.get("sales")
            if raw_value in (None, ""):
                continue
            received += 1
            period = item["period"]
            sid = f"EIA_RETAIL_SALES_US_ALL"
            existing = db.scalar(select(Observation).where(
                Observation.source == "EIA",
                Observation.series_id == sid,
                Observation.period == period
            ))
            value = float(raw_value)
            if existing:
                existing.value = value
            else:
                db.add(Observation(
                    source="EIA", indicator_code="ELECTRICITY_RETAIL_SALES",
                    series_id=sid, metric_name="Electricity sales to ultimate customers, all sectors",
                    period=period, value=value, unit=item.get("sales-units", "million kilowatthours"),
                    geography="United States", source_url="https://www.eia.gov/electricity/data.php"
                ))
                inserted += 1
        run.status = "success"; run.records_received = received; run.records_inserted = inserted
        run.finished_at = datetime.now(timezone.utc); run.message = f"Monthly data {start} to {end}"
        db.commit()
        return {"source":"EIA","status":"success","received":received,"inserted":inserted}
    except Exception as exc:
        db.rollback()
        run.status = "failed"; run.message = str(exc); run.finished_at = datetime.now(timezone.utc)
        db.add(run); db.commit()
        raise
