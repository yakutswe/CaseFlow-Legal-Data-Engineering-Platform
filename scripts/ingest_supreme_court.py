from app.db.session import SessionLocal
from ingestion.pipelines.source_pipeline import ingest_source
from ingestion.sources.supreme_court_source import SupremeCourtSource


db = SessionLocal()

try:
    source = SupremeCourtSource()

    results = ingest_source(
        db,
        source,
        min_expected_records=10,
    )

    created = [
        r for r in results
        if r["status"] == "created"
    ]

    updated = [
        r for r in results
        if r["status"] == "updated"
    ]

    duplicates = [
        r for r in results
        if r["status"] == "duplicate"
    ]

    failed = [
        r for r in results
        if r["status"] == "failed"
    ]

    print(f"Created: {len(created)}")
    print(f"Updated: {len(updated)}")
    print(f"Duplicates: {len(duplicates)}")
    print(f"Failed: {len(failed)}")

finally:
    db.close()