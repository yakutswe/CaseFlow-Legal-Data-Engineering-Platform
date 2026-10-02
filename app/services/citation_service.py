from sqlalchemy.orm import Session

from app.models import Citation
from app.repositories.citation_repository import (
    CitationRepository,
)
from ingestion.parsers.citation_parser import (
    extract_citations,
)


class CitationService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.repository = CitationRepository(
            db
        )

    def rebuild_for_case(
        self,
        *,
        case_id: int,
        opinion_text: str,
    ) -> int:
        parsed = extract_citations(
            opinion_text
        )

        self.repository.delete_for_case(
            case_id
        )

        for item in parsed:
            citation = Citation(
                citing_case_id=case_id,
                cited_case_name=(
                    item.cited_case_name
                ),
                volume=item.volume,
                reporter=item.reporter,
                page=item.page,
                pin_cite=item.pin_cite,
                year=item.year,
            )

            self.repository.create(
                citation
            )

        self.db.commit()

        return len(parsed)