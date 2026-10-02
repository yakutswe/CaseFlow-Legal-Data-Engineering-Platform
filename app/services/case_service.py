from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Any

from app.models import Case, Court
from app.repositories.case_repository import CaseRepository


class CaseService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CaseRepository(db)

    def create_case(self, payload: Any) -> Case:
        court = self.db.get(Court, payload.court_id)

        if court is None:
            raise ValueError("Court not found")

        case = Case(**payload.model_dump())

        try:
            return self.repository.create(case)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Case already exists")