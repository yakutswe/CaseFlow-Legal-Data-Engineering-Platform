from datetime import date

from pydantic import BaseModel


class SearchResult(BaseModel):
    case_id: int
    case_name: str
    decision_date: date | None
    source_url: str
    rank: float
    snippet: str