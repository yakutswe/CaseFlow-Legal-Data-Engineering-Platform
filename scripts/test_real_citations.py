from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Case
from ingestion.parsers.citation_parser import (
    extract_citations,
)


db = SessionLocal()

try:
    case = db.execute(
        select(Case).where(
            Case.case_name
            == "Trump v. California"
        )
    ).scalar_one()

    citations = extract_citations(
        case.opinion_text
    )

    print(
        f"Total citations: {len(citations)}"
    )

    for citation in citations[:30]:
        print(citation)

finally:
    db.close()