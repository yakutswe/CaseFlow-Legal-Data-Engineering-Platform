from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models import Case, Citation, Court, IngestionJob
from app.schemas.case import CaseCreate, CaseRead
from app.schemas.court import CourtCreate, CourtRead
from app.services.case_service import CaseService

router = APIRouter()


@router.post("/courts", response_model=CourtRead, status_code=201)
def create_court(payload: CourtCreate, db: Session = Depends(get_db)):
    court = Court(**payload.model_dump())
    db.add(court)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Court already exists")
    db.refresh(court)
    return court


@router.get("/courts", response_model=list[CourtRead])
def list_courts(db: Session = Depends(get_db)):
    return db.execute(select(Court).order_by(Court.name)).scalars().all()


@router.post("/cases", response_model=CaseRead, status_code=201)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    service = CaseService(db)
    try:
        return service.create_case(payload)
    except ValueError as exc:
        message = str(exc)
        if message == "Court not found":
            raise HTTPException(status_code=404, detail=message)
        raise HTTPException(status_code=409, detail=message)


@router.get("/cases", response_model=list[CaseRead])
def list_cases(
    court_id: int | None = None,
    decision_date_from: date | None = None,
    decision_date_to: date | None = None,
    case_name: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Case)
    if court_id is not None:
        stmt = stmt.where(Case.court_id == court_id)
    if decision_date_from is not None:
        stmt = stmt.where(Case.decision_date >= decision_date_from)
    if decision_date_to is not None:
        stmt = stmt.where(Case.decision_date <= decision_date_to)
    if case_name:
        stmt = stmt.where(Case.case_name.ilike(f"%{case_name}%"))
    stmt = stmt.order_by(Case.decision_date.desc()).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    cases = db.scalar(select(func.count(Case.id))) or 0
    courts = db.scalar(select(func.count(Court.id))) or 0
    citations = db.scalar(select(func.count(Citation.id))) or 0
    jobs = db.scalar(select(func.count(IngestionJob.id))) or 0
    failed = db.scalar(
        select(func.coalesce(func.sum(IngestionJob.failed_count), 0))
    ) or 0
    latest = db.execute(
        select(IngestionJob).order_by(IngestionJob.started_at.desc()).limit(1)
    ).scalar_one_or_none()
    return {
        "cases": cases,
        "courts": courts,
        "citations": citations,
        "ingestion_jobs": jobs,
        "failed_records": int(failed),
        "latest_job": None if latest is None else {
            "source_name": latest.source_name,
            "status": latest.status,
            "fetched_count": latest.fetched_count,
            "created_count": latest.created_count,
            "updated_count": latest.updated_count,
            "duplicate_count": latest.duplicate_count,
            "failed_count": latest.failed_count,
            "started_at": latest.started_at,
            "finished_at": latest.finished_at,
        },
    }


@router.get("/dashboard/recent-cases")
def recent_cases(limit: int = Query(default=8, ge=1, le=25), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Case, Court)
        .join(Court, Case.court_id == Court.id)
        .order_by(Case.decision_date.desc(), Case.id.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": case.id,
            "case_name": case.case_name,
            "court": court.abbreviation,
            "court_name": court.name,
            "decision_date": case.decision_date,
            "docket_number": case.docket_number,
            "source_url": case.source_url,
        }
        for case, court in rows
    ]


@router.get("/dashboard/top-citations")
def top_citations(limit: int = Query(default=8, ge=1, le=25), db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Citation.cited_case_name,
            Citation.volume,
            Citation.reporter,
            Citation.page,
            func.count(Citation.id).label("citation_count"),
        )
        .group_by(
            Citation.cited_case_name,
            Citation.volume,
            Citation.reporter,
            Citation.page,
        )
        .order_by(func.count(Citation.id).desc())
        .limit(limit)
    ).all()
    return [
        {
            "case_name": row.cited_case_name or "Unresolved citation",
            "citation": f"{row.volume} {row.reporter} {row.page}",
            "count": row.citation_count,
        }
        for row in rows
    ]


@router.get("/dashboard/ingestion-jobs")
def ingestion_jobs(limit: int = Query(default=6, ge=1, le=25), db: Session = Depends(get_db)):
    jobs = db.execute(
        select(IngestionJob).order_by(IngestionJob.started_at.desc()).limit(limit)
    ).scalars().all()
    return [
        {
            "id": job.id,
            "source_name": job.source_name,
            "status": job.status,
            "fetched_count": job.fetched_count,
            "created_count": job.created_count,
            "updated_count": job.updated_count,
            "duplicate_count": job.duplicate_count,
            "failed_count": job.failed_count,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
        }
        for job in jobs
    ]
