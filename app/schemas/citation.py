from pydantic import BaseModel, ConfigDict


class CitationRead(BaseModel):
    id: int
    citing_case_id: int
    cited_case_name: str | None
    volume: int
    reporter: str
    page: int
    pin_cite: int | None
    year: int | None

    model_config = ConfigDict(
        from_attributes=True
    )