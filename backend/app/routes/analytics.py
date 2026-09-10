"""Analytics and dashboard data routes."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from pydantic import BaseModel

from app.database import get_session
from app.models import Student, Class, Observation
from app.services import CalculationService

router = APIRouter()

class MeasureStats(BaseModel):
    measure: str
    performance_percentage: float | None
    ones_observed: int
    zeros_not_observed: int
    not_applicable: int
    band: str
    status: str

class StudentAnalytics(BaseModel):
    student_id: str
    student_name: str
    overall_performance: float | None
    performance_band: str
    performance_by_measure: list[MeasureStats]
    attendance_rate: float | None
    days_observed: int
    days_absent: int
    days_since_last_observation: int | None
    recommended_next_steps: str

class StudentSummary(BaseModel):
    student_id: str
    student_name: str
    achievement_percentage: float | None
    attendance_percentage: float | None
    band: str
    status: str

class ClassAnalytics(BaseModel):
    class_code: str
    class_name: str
    total_students: int
    students_with_observations: int
    average_performance: float | None
    performance_distribution: dict[str, int]
    student_summaries: list[StudentSummary]

@router.get("/student/{student_id}", response_model=StudentAnalytics)
async def get_student_analytics(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get student analytics data for dashboard."""
    # Verify student exists
    query = select(Student).where(Student.student_id == student_id)
    result = await session.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Calculate overall performance
    overall_perf, _, _, _, _ = await CalculationService.calculate_performance(
        session, student_id=student_id
    )

    # Get measure breakdown
    measure_breakdown = await CalculationService.get_student_measure_breakdown(session, student_id)

    # Calculate attendance
    attendance = await CalculationService.calculate_attendance_rate(session, student_id)
    days_observed = await CalculationService.get_total_observation_days(session, student_id)
    days_absent = await CalculationService.get_days_absent(session, student_id)
    days_since = await CalculationService.get_days_since_last_observation(session, student_id)

    # Get performance band
    band_name, _ = CalculationService.get_performance_band(overall_perf)

    # Get recommended next steps
    next_steps = CalculationService.get_recommended_next_steps(overall_perf)

    return {
        "student_id": student_id,
        "student_name": student.name,
        "overall_performance": overall_perf,
        "performance_band": band_name,
        "performance_by_measure": measure_breakdown,
        "attendance_rate": attendance,
        "days_observed": days_observed,
        "days_absent": days_absent,
        "days_since_last_observation": days_since,
        "recommended_next_steps": next_steps
    }

@router.get("/class/{class_code}", response_model=ClassAnalytics)
async def get_class_analytics(
    class_code: str,
    session: AsyncSession = Depends(get_session)
):
    """Get class analytics data for dashboard."""
    # Verify class exists
    class_query = select(Class).where(Class.class_code == class_code)
    class_result = await session.execute(class_query)
    class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Get students in class
    student_query = select(Student).where(Student.primary_class == class_code)
    student_result = await session.execute(student_query)
    students = student_result.scalars().all()

    # Calculate analytics for each student
    student_summaries = []
    performances = []
    students_with_obs = 0

    for student in students:
        perf, _, _, _, _ = await CalculationService.calculate_performance(
            session, student_id=student.student_id
        )

        attendance = await CalculationService.calculate_attendance_rate(
            session, student_id=student.student_id
        )

        # Determine status
        if perf is None:
            status = "⚠️ No Data"
        elif perf < 50:
            status = "🔴 Below 50%"
        elif perf < 75:
            status = "⚠️ Watch"
        else:
            status = "✓ Good"

        band_name, _ = CalculationService.get_performance_band(perf)

        student_summaries.append({
            "student_id": student.student_id,
            "student_name": student.name,
            "achievement_percentage": perf,
            "attendance_percentage": attendance,
            "band": band_name,
            "status": status
        })

        if perf is not None:
            performances.append(perf)
            students_with_obs += 1

    # Calculate average performance
    avg_performance = sum(performances) / len(performances) if performances else None

    # Calculate performance distribution
    distribution = {
        "Exemplary": 0,
        "Proficient": 0,
        "Developing": 0,
        "Emerging": 0,
        "Beginning": 0,
        "Needs Intensive Support": 0
    }

    for perf in performances:
        band_name, _ = CalculationService.get_performance_band(perf)
        if band_name in distribution:
            distribution[band_name] += 1

    return {
        "class_code": class_code,
        "class_name": class_obj.class_name,
        "total_students": len(students),
        "students_with_observations": students_with_obs,
        "average_performance": avg_performance,
        "performance_distribution": distribution,
        "student_summaries": student_summaries
    }
