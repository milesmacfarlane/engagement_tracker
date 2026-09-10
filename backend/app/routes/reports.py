"""Report generation routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

router = APIRouter()

@router.get("/student/{student_id}")
async def generate_student_report(
    student_id: str,
    format: str = Query("pdf", regex="^(pdf|html)$"),
    session: AsyncSession = Depends(get_session)
):
    """Generate student report (PDF or HTML)."""
    # TODO: Integrate with ReportLab for PDF generation
    return {"message": "Report generation in progress"}

@router.get("/class/{class_code}")
async def generate_class_report(
    class_code: str,
    format: str = Query("pdf", regex="^(pdf|html)$"),
    session: AsyncSession = Depends(get_session)
):
    """Generate class report (PDF or HTML)."""
    # TODO: Integrate with ReportLab for PDF generation
    return {"message": "Report generation in progress"}
