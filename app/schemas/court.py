from pydantic import BaseModel, ConfigDict


class CourtCreate(BaseModel):
    name: str
    abbreviation: str
    jurisdiction: str
    level: str


class CourtRead(CourtCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
    