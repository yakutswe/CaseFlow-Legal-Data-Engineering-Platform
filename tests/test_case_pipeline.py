from datetime import date

from app.db.session import SessionLocal
from app.models import Case
from ingestion.pipelines.case_pipeline import ingest_case


def test_create_duplicate_and_update_case():
    db = SessionLocal()

    external_id = "pytest-case-001"

    try:
        existing = (
            db.query(Case)
            .filter(Case.external_id == external_id)
            .first()
        )

        if existing:
            db.delete(existing)
            db.commit()

        first_result = ingest_case(
            db=db,
            external_id=external_id,
            case_name="Pytest Example Case",
            court_id=1,
            decision_date=date(2026, 1, 1),
            docket_number="TEST-001",
            opinion_text="Original opinion text.",
            source_url="https://example.com/test-case",
        )

        assert first_result["status"] == "created"

        duplicate_result = ingest_case(
            db=db,
            external_id=external_id,
            case_name="Pytest Example Case",
            court_id=1,
            decision_date=date(2026, 1, 1),
            docket_number="TEST-001",
            opinion_text="Original opinion text.",
            source_url="https://example.com/test-case",
        )

        assert duplicate_result["status"] == "duplicate"

        update_result = ingest_case(
            db=db,
            external_id=external_id,
            case_name="Pytest Example Case",
            court_id=1,
            decision_date=date(2026, 1, 1),
            docket_number="TEST-001",
            opinion_text="Updated opinion text.",
            source_url="https://example.com/test-case",
        )

        assert update_result["status"] == "updated"

    finally:
        case = (
            db.query(Case)
            .filter(Case.external_id == external_id)
            .first()
        )

        if case:
            db.delete(case)
            db.commit()

        db.close()