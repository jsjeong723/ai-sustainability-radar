from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from pathlib import Path
from .db import init_db, SessionLocal, Observation, CollectionRun
from .collectors import collect_bls, collect_eia

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="AI Sustainability Radar Data API", version="0.1.0", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status":"ok","service":"ai-sustainability-radar-data-api"}

@app.post("/api/collect/bls")
async def run_bls(db: Session = Depends(get_db)):
    try:
        return await collect_bls(db)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"BLS collection failed: {exc}")

@app.post("/api/collect/eia")
async def run_eia(db: Session = Depends(get_db)):
    try:
        return await collect_eia(db)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"EIA collection failed: {exc}")

@app.post("/api/collect/all")
async def run_all(db: Session = Depends(get_db)):
    results = []
    errors = []
    for name, fn in (("BLS", collect_bls), ("EIA", collect_eia)):
        try:
            results.append(await fn(db))
        except Exception as exc:
            errors.append({"source":name,"error":str(exc)})
    return {"results":results,"errors":errors,"status":"partial" if errors else "success"}

@app.get("/api/observations")
def observations(source: str | None = None, indicator: str | None = None, limit: int = 500, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 5000))
    stmt = select(Observation)
    if source:
        stmt = stmt.where(Observation.source == source.upper())
    if indicator:
        stmt = stmt.where(Observation.indicator_code == indicator.upper())
    rows = db.scalars(stmt.order_by(Observation.period.asc()).limit(limit)).all()
    return [{
        "id":r.id, "source":r.source, "indicator_code":r.indicator_code,
        "series_id":r.series_id, "metric_name":r.metric_name, "period":r.period,
        "value":r.value, "unit":r.unit, "geography":r.geography,
        "source_url":r.source_url, "footnote":r.footnote
    } for r in rows]

@app.get("/api/status")
def status(db: Session = Depends(get_db)):
    runs = db.scalars(select(CollectionRun).order_by(desc(CollectionRun.started_at)).limit(10)).all()
    count = len(db.scalars(select(Observation.id)).all())
    return {
        "observation_count":count,
        "latest_runs":[{
            "source":r.source,"status":r.status,"records_received":r.records_received,
            "records_inserted":r.records_inserted,"message":r.message,
            "started_at":r.started_at.isoformat() if r.started_at else None,
            "finished_at":r.finished_at.isoformat() if r.finished_at else None
        } for r in runs]
    }

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html = Path(__file__).parent / "static" / "index.html"
    return html.read_text(encoding="utf-8")
