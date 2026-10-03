from app.db.session import SessionLocal
from ingestion.pipelines.source_pipeline import ingest_source
from ingestion.sources.sample_legal_source import SampleLegalSource


db = SessionLocal()

try:
    source = SampleLegalSource()

    results = ingest_source(
        db,
        source,
    )

    print(results)

finally:
    db.close()