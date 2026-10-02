from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    external_id: str
    case_name: str
    court_id: int
    decision_date: date | None = None
    docket_number: str | None = None
    opinion_text: str
    source_url: str
    content_hash: str


class CaseRead(CaseCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)