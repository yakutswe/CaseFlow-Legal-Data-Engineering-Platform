from datetime import date

from app.db.session import SessionLocal
from ingestion.pipelines.case_pipeline import ingest_case


db = SessionLocal()

try:
    result = ingest_case(
        db,
        external_id="scotus-miranda-v-arizona-1966",
        case_name="Miranda v. Arizona",
        court_id=1,
        decision_date=date(1966, 6, 13),
        docket_number="759",
        opinion_text="""
        Sample opinion text for Miranda v. Arizona.
        This record is being used to test the CaseFlow ingestion pipeline.
        """,
        source_url="https://example.com/miranda-v-arizona",
    )

    print(result)

finally:
    db.close()