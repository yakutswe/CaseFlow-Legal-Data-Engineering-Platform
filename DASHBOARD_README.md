# CaseFlow dashboard

The project now includes a lightweight frontend served directly by FastAPI.

## Run locally

```powershell
cd C:\Users\yakut\Desktop\caseflow\caseflow
docker compose up -d
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000/
- Swagger API: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

The dashboard reads live data from PostgreSQL through the CaseFlow API. If the database is unavailable, the UI remains visible and shows an unavailable state rather than fake data.
