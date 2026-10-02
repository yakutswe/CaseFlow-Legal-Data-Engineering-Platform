from fastapi import APIRouter, FastAPI

try:
    from app.api.routes import router
except ImportError:
    router = APIRouter()


app = FastAPI(
    title="CaseFlow",
    description="Legal data ingestion and citation intelligence platform",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "caseflow",
    }