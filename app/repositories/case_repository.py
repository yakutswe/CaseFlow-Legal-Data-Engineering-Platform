from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Case


class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, case_id: int) -> Case | None:
        return self.db.get(Case, case_id)

    def get_by_external_id(self, external_id: str) -> Case | None:
        stmt = select(Case).where(Case.external_id == external_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_content_hash(
        self,
        content_hash: str,
    ) -> Case | None:
        stmt = select(Case).where(
            Case.content_hash == content_hash
        )

        return self.db.execute(
            stmt
        ).scalar_one_or_none()

    def list(
        self,
        *,
        court_id: int | None = None,
        case_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Case]:
        stmt = select(Case)

        if court_id is not None:
            stmt = stmt.where(Case.court_id == court_id)

        if case_name:
            stmt = stmt.where(Case.case_name.ilike(f"%{case_name}%"))

        stmt = (
            stmt
            .order_by(Case.decision_date.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.execute(stmt).scalars().all())

    def create(self, case: Case) -> Case:
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case