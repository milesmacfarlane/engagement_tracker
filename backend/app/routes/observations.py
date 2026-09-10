"""Observation management routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from pydantic import BaseModel
from datetime import date
import csv
import io

from app.database import get_session
from app.models import Observation, Student, Class
from app.services import CalculationService

router = APIRouter()

class ObservationRecord(BaseModel):
    date: date
    class_code: str
    student_id: str
    measure_name: str
    value: str  # "1", "0", or "-"

    class Config:
        from_attributes = True

class BatchObservationsRequest(BaseModel):
    observations: list[ObservationRecord]

class ObservationListResponse(BaseModel):
    data: list[ObservationRecord]
    total: int

@router.get("/", response_model=ObservationListResponse)
async def list_observations(
    date_filter: date | None = Query(None),
    class_code: str | None = None,
    student_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List observations with optional filters."""
    query = select(Observation)

    if date_filter:
        query = query.where(Observation.date == date_filter)
    if class_code:
        query = query.where(Observation.class_code == class_code)
    if student_id:
        query = query.where(Observation.student_id == student_id)

    # Get total count
    count_result = await session.execute(query)
    total = len(count_result.scalars().all())

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    observations = result.scalars().all()

    return {
        "data": [ObservationRecord.from_orm(o) for o in observations],
        "total": total
    }

@router.post("/batch")
async def batch_save_observations(
    request: BatchObservationsRequest,
    session: AsyncSession = Depends(get_session)
):
    """Batch save observations from entry log."""
    errors = []
    saved = 0

    for obs in request.observations:
        try:
            # Validate value
            if not CalculationService.validate_observation_value(obs.value):
                errors.append(f"Invalid value '{obs.value}' for student {obs.student_id}")
                continue

            # Verify student and class exist
            student_query = select(Student).where(Student.student_id == obs.student_id)
            student_result = await session.execute(student_query)
            if not student_result.scalar_one_or_none():
                errors.append(f"Student {obs.student_id} not found")
                continue

            class_query = select(Class).where(Class.class_code == obs.class_code)
            class_result = await session.execute(class_query)
            if not class_result.scalar_one_or_none():
                errors.append(f"Class {obs.class_code} not found")
                continue

            # Create observation
            observation = Observation(
                date=obs.date,
                class_code=obs.class_code,
                student_id=obs.student_id,
                measure_name=obs.measure_name,
                value=obs.value
            )
            session.add(observation)
            saved += 1
        except Exception as e:
            errors.append(f"Error saving observation for {obs.student_id}: {str(e)}")

    await session.commit()

    return {
        "saved": saved,
        "errors": errors,
        "total_errors": len(errors)
    }

@router.get("/export")
async def export_observations(
    date_filter: date | None = Query(None),
    class_code: str | None = None,
    session: AsyncSession = Depends(get_session)
):
    """Export observations as CSV."""
    query = select(Observation)

    if date_filter:
        query = query.where(Observation.date == date_filter)
    if class_code:
        query = query.where(Observation.class_code == class_code)

    result = await session.execute(query)
    observations = result.scalars().all()

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['date', 'class_code', 'student_id', 'measure_name', 'value'])
    writer.writeheader()

    for obs in observations:
        writer.writerow({
            'date': obs.date.isoformat(),
            'class_code': obs.class_code,
            'student_id': obs.student_id,
            'measure_name': obs.measure_name,
            'value': obs.value
        })

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=observations.csv"}
    )
