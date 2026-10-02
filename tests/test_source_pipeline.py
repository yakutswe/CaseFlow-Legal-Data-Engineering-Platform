import pytest

from app.db.session import SessionLocal
from ingestion.pipelines.source_pipeline import ingest_source


class BrokenSource:
    name = "broken-source"

    def fetch(self):
        return []


def test_suspicious_low_record_count():
    db = SessionLocal()

    try:
        with pytest.raises(
            RuntimeError,
            match="Suspiciously low record count",
        ):
            ingest_source(
                db=db,
                source=BrokenSource(),
                min_expected_records=10,
            )
    finally:
        db.close()