from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.citation import CitationRead
from app.schemas.search import SearchResult

from app.db.deps import get_db
from app.models import Case, Citation, Court
from app.schemas.citation import CitationRead
from app.schemas.case import CaseCreate, CaseRead
from app.schemas.court import CourtCreate, CourtRead
from app.services.case_service import CaseService


router = APIRouter()


@router.post("/courts", response_model=CourtRead)
def create_court(
    payload: CourtCreate,
    db: Session = Depends(get_db),
):
    court = Court(**payload.model_dump())

    db.add(court)
    db.commit()
    db.refresh(court)

    return court

@router.post(
    "/cases",
    response_model=CaseRead,
    status_code=201,
)
def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
):
    service = CaseService(db)

    try:
        return service.create_case(payload)
    except ValueError as exc:
        message = str(exc)

        if message == "Court not found":
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=409,
            detail=message,
        )

    db.refresh(case)

    return case


@router.get(
    "/cases/{case_id}/citations",
    response_model=list[CitationRead],
)
def get_case_citations(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = db.get(Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    stmt = (
        select(Citation)
        .where(
            Citation.citing_case_id == case_id
        )
        .order_by(Citation.id)
    )

    return list(
        db.scalars(stmt).all()
    )


@router.get("/citations/top")
def get_top_citations(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Citation.cited_case_name,
            func.count(
                Citation.id
            ).label("citation_count"),
        )
        .where(
            Citation.cited_case_name.is_not(None)
        )
        .group_by(
            Citation.cited_case_name
        )
        .order_by(
            func.count(
                Citation.id
            ).desc()
        )
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "cited_case_name":
                row.cited_case_name,
            "citation_count":
                row.citation_count,
        }
        for row in rows
    ]


@router.get(
    "/search",
    response_model=list[SearchResult],
)
def search_cases(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    search_vector = func.to_tsvector(
        "english",
        Case.opinion_text,
    )

    search_query = func.plainto_tsquery(
        "english",
        q,
    )

    rank = func.ts_rank(
        search_vector,
        search_query,
    )

    snippet = func.ts_headline(
        "english",
        Case.opinion_text,
        search_query,
        "StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15",
    )

    stmt = (
        select(
            Case.id.label("case_id"),
            Case.case_name,
            Case.decision_date,
            Case.source_url,
            rank.label("rank"),
            snippet.label("snippet"),
        )
        .where(
            search_vector.op("@@")(search_query)
        )
        .order_by(rank.desc())
        .offset(offset)
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "case_id": row.case_id,
            "case_name": row.case_name,
            "decision_date": row.decision_date,
            "source_url": row.source_url,
            "rank": float(row.rank or 0),
            "snippet": row.snippet or "",
        }
        for row in rows
    ]