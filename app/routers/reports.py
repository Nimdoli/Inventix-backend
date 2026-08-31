import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Report

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportBase(BaseModel):
    category: str  # "sales" | "inventory"
    file_name: str


class ReportCreate(ReportBase):
    file_url: Optional[str] = None


class ReportOut(ReportBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    file_url: Optional[str] = None


class ScheduleRequest(BaseModel):
    category: str
    cron: str  # e.g. "0 10 * * MON" for "next Monday 10AM"-style recurring reports


@router.get("", response_model=list[ReportOut])
def list_reports(
    category: Optional[str] = None,  # "sales reports" | "inventory reports"
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Report)
    if category == "sales reports":
        query = query.filter(Report.category == "sales")
    elif category == "inventory reports":
        query = query.filter(Report.category == "inventory")
    return query.order_by(Report.generated_at.desc()).all()


@router.post("", response_model=ReportOut, status_code=201)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    report = Report(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}/download")
def download_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.file_url:
        raise HTTPException(status_code=404, detail="Report file not found")
    # file_url points at Supabase Storage — redirect the client to the actual file
    return RedirectResponse(report.file_url)


@router.post("/schedule", status_code=202)
def schedule_report(payload: ScheduleRequest):
    # Placeholder: wire this to a scheduled job (e.g. Supabase Edge Function on a
    # cron trigger, or a background task) once report generation logic exists.
    return {"scheduled": True, "category": payload.category, "cron": payload.cron}
