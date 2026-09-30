from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Case
from app.services.citation_service import (
    CitationService,
)


db = SessionLocal()

try:
    cases = list(
        db.execute(
            select(Case)
            .order_by(Case.id)
        )
        .scalars()
        .all()
    )

    service = CitationService(db)

    total_citations = 0

    for case in cases:
        count = service.rebuild_for_case(
            case_id=case.id,
            opinion_text=case.opinion_text,
        )

        total_citations += count

        print(
            f"{case.id}: "
            f"{case.case_name} "
            f"-> {count} citations"
        )

    print()
    print(
        f"Cases processed: "
        f"{len(cases)}"
    )

    print(
        f"Citations extracted: "
        f"{total_citations}"
    )

finally:
    db.close()