import hashlib

from sqlalchemy.orm import Session

from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseCreate as CaseCreateSchema
from app.services.case_service import CaseService


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()


def generate_content_hash(text: str) -> str:
    normalized = normalize_text(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def ingest_case(
    db: Session,
    *,
    external_id: str,
    case_name: str,
    court_id: int,
    decision_date,
    docket_number: str | None,
    opinion_text: str,
    source_url: str,
):
    repository = CaseRepository(db)
    service = CaseService(db)

    # 1. Normalize opinion and generate hash
    normalized_opinion = normalize_text(
        opinion_text
    )

    content_hash = generate_content_hash(
        normalized_opinion
    )

    # 2. Look for existing case by source ID
    existing = repository.get_by_external_id(
        external_id
    )

    if existing is not None:

        # Same source ID + same content
        if existing.content_hash == content_hash:
            return {
                "status": "duplicate",
                "reason": "unchanged",
                "case_id": existing.id,
            }

        # Prevent another case from already
        # owning this content hash
        existing_by_hash = (
            repository.get_by_content_hash(
                content_hash
            )
        )

        if (
            existing_by_hash is not None
            and existing_by_hash.id != existing.id
        ):
            return {
                "status": "duplicate",
                "reason": "content_hash",
                "case_id": existing_by_hash.id,
            }

        # 3. Existing source ID but content changed:
        # update the record
        existing.case_name = normalize_text(
            case_name
        )

        existing.court_id = court_id
        existing.decision_date = decision_date

        existing.docket_number = (
            docket_number.strip()
            if docket_number
            else None
        )

        existing.opinion_text = (
            normalized_opinion
        )

        existing.source_url = (
            source_url.strip()
        )

        existing.content_hash = content_hash

        db.commit()
        db.refresh(existing)

        return {
            "status": "updated",
            "case_id": existing.id,
            "content_hash": (
                existing.content_hash
            ),
        }

    # 4. New external ID:
    # check whether identical content exists
    existing_by_hash = (
        repository.get_by_content_hash(
            content_hash
        )
    )

    if existing_by_hash is not None:
        return {
            "status": "duplicate",
            "reason": "content_hash",
            "case_id": existing_by_hash.id,
        }

    # 5. Build validated payload
    payload = CaseCreateSchema(
        external_id=external_id.strip(),
        case_name=normalize_text(
            case_name
        ),
        court_id=court_id,
        decision_date=decision_date,
        docket_number=(
            docket_number.strip()
            if docket_number
            else None
        ),
        opinion_text=normalized_opinion,
        source_url=source_url.strip(),
        content_hash=content_hash,
    )

    # 6. Create new case
    case = service.create_case(
        payload
    )

    return {
        "status": "created",
        "case_id": case.id,
        "content_hash": case.content_hash,
    }