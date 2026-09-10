"""Observation management routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date

from app.database import get_session

router = APIRouter()

class ObservationRecord(BaseModel):
    date: date
    class_code: str
    student_id: str
    measure_name: str
    value: str  # "1", "0", or "-"

class BatchObservationsRequest(BaseModel):
    observations: list[ObservationRecord]

@router.get("/")
async def list_observations(
    date: date = None,
    class_code: str = None,
    student_id: str = None,
    session: AsyncSession = Depends(get_session)
):
    """List observations with optional filters."""
    # TODO: Implement with filters
    return []

@router.post("/batch")
async def batch_save_observations(
    request: BatchObservationsRequest,
    session: AsyncSession = Depends(get_session)
):
    """Batch save observations from entry log."""
    # TODO: Implement batch insert
    return {"saved": len(request.observations)}

@router.get("/export")
async def export_observations(session: AsyncSession = Depends(get_session)):
    """Export observations as CSV."""
    # TODO: Implement CSV export
    return {"message": "Export in progress"}
