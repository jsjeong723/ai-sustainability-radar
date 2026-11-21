# BLS + EIA collector add-on

This is a drop-in first implementation for the AI Sustainability Radar repository. It provides:
- BLS v2 collection for total nonfarm employment, unemployment rate, and average hourly earnings.
- EIA v2 monthly U.S. electricity retail sales (all sectors).
- SQLite by default for local verification; PostgreSQL can be used by setting `DATABASE_URL`.
- FastAPI endpoints and a small dashboard served at `/`.
- A GitHub Actions workflow that triggers collection on a deployed instance.

## 1. Add these files to the repository

Copy the contents of this package into the repository root, preserving paths. Existing files should be reviewed before replacement.

## 2. Configure EIA API key

Register for a free EIA API key:
https://www.eia.gov/opendata/register.php

Copy `backend/.env.example` to `backend/.env` and set `EIA_API_KEY`. Do not commit `.env`.

BLS v2 can be called without a registration key for limited public use. Add `BLS_API_KEY` if you register for one.

## 3. Run locally

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add EIA_API_KEY
uvicorn app.main:app --reload
```

Open:
- Dashboard: http://127.0.0.1:8000/
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Click **지금 수집** or run:
```bash
curl -X POST http://127.0.0.1:8000/api/collect/all
```

## 4. GitHub Actions deployment

The included workflow calls a deployed API. Configure repository Actions secrets:
- `RADAR_API_URL`: base URL of the deployed FastAPI service, without trailing slash.
- `RADAR_CRON_TOKEN`: optional bearer token if authentication middleware is added.

The starter API currently does not enforce `RADAR_CRON_TOKEN`. Do not expose the collection endpoint publicly until authentication or network restrictions are added. For an initial private test, use manual collection from a trusted local environment. Before enabling the scheduled workflow on a public deployment, add authentication.

## 5. What is collected

BLS:
- `CES0000000001`: Total nonfarm employment (thousands of persons)
- `LNS14000000`: Unemployment rate (percent)
- `CES0500000003`: Average hourly earnings, total private (USD/hour)

EIA:
- Monthly electricity sales to ultimate customers, U.S. total, all sectors (million kilowatthours).

Important: EIA electricity retail sales is a national electricity-use proxy, not a measurement of AI/data-center electricity use. It must not be described as AI-attributable consumption.

## 6. Limitations before production

- The included dashboard is a functional starter screen, not the final Next.js UI.
- SQLite is suitable for local testing only; use PostgreSQL for shared research operation.
- Add authentication, authorization, migrations, monitoring, backup, and rate-limit handling before public deployment.
- EIA API key is required. Live data collection cannot succeed until it is configured.
- The code has not been executed against live BLS/EIA services in this environment. Verify first-run responses and API access locally.
