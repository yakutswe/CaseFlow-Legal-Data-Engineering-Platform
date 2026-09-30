from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_job import IngestionJob
from ingestion.pipelines.case_pipeline import ingest_case
from ingestion.sources.base import LegalSource


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None

    value = value.strip()

    for fmt in ("%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {value}"
    )


def ingest_source(
    db: Session,
    source: LegalSource,
    *,
    min_expected_records: int = 1,
) -> list[dict[str, Any]]:
    job = IngestionJob(
        source_name=source.__class__.__name__,
        status="running",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    results: list[dict[str, Any]] = []

    try:
        raw_records = source.fetch()

        job.fetched_count = len(raw_records)

        # Detect silent scraper failure
        if len(raw_records) < min_expected_records:
            job.status = "suspicious"
            job.finished_at = datetime.now(UTC)

            db.commit()

            raise RuntimeError(
                f"Suspiciously low record count: "
                f"{len(raw_records)} < {min_expected_records}"
            )

        for record in raw_records:
            try:
                result = ingest_case(
                    db,
                    external_id=record["external_id"],
                    case_name=record["case_name"],
                    court_id=record["court_id"],
                    decision_date=parse_date(
                        record.get("decision_date")
                    ),
                    docket_number=record.get(
                        "docket_number"
                    ),
                    opinion_text=record["opinion_text"],
                    source_url=record["source_url"],
                )

                results.append(result)

                if result["status"] == "created":
                    job.created_count += 1

                elif result["status"] == "updated":
                    job.updated_count += 1

                elif result["status"] == "duplicate":
                    job.duplicate_count += 1

            except Exception as exc:
                job.failed_count += 1

                results.append(
                    {
                        "status": "failed",
                        "external_id": record.get(
                            "external_id"
                        ),
                        "error": str(exc),
                    }
                )

        if job.failed_count == 0:
            job.status = "completed"
        else:
            job.status = "completed_with_errors"

        job.finished_at = datetime.now(UTC)

        db.commit()

        return results

    except RuntimeError:
        # Preserve "suspicious" if already set.
        if job.status != "suspicious":
            job.status = "failed"
            job.finished_at = datetime.now(UTC)
            db.commit()

        raise

    except Exception:
        job.status = "failed"
        job.finished_at = datetime.now(UTC)
        db.commit()
        raise