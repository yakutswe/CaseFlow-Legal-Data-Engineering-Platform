from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Citation


class CitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_case(
        self,
        case_id: int,
    ) -> list[Citation]:
        stmt = (
            select(Citation)
            .where(
                Citation.citing_case_id
                == case_id
            )
            .order_by(Citation.id)
        )

        return list(
            self.db.execute(
                stmt
            ).scalars().all()
        )

    def delete_for_case(
        self,
        case_id: int,
    ) -> None:
        stmt = delete(Citation).where(
            Citation.citing_case_id
            == case_id
        )

        self.db.execute(stmt)

    def create(
        self,
        citation: Citation,
    ) -> Citation:
        self.db.add(citation)

        return citation