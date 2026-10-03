from app.db.session import SessionLocal
from ingestion.pipelines.source_pipeline import ingest_source
from ingestion.sources.broken_source import BrokenSource


db = SessionLocal()

try:
    source = BrokenSource()

    ingest_source(
        db,
        source,
        min_expected_records=10,
    )

finally:
    db.close()