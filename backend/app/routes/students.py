"""Student management routes."""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from pydantic import BaseModel
import csv
import io

from app.database import get_session
from app.models import Student, Class

router = APIRouter()

class StudentSchema(BaseModel):
    student_id: str
    name: str
    primary_class: str

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    data: list[StudentSchema]
    total: int
    page: int
    per_page: int

@router.get("/", response_model=StudentListResponse)
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    class_code: str | None = None,
    session: AsyncSession = Depends(get_session)
):
    """List students with pagination."""
    query = select(Student)

    if class_code:
        query = query.where(Student.primary_class == class_code)

    # Get total count
    count_result = await session.execute(select(Student))
    total = len(count_result.scalars().all())

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    students = result.scalars().all()

    return {
        "data": [StudentSchema.from_orm(s) for s in students],
        "total": total,
        "page": skip // limit,
        "per_page": limit
    }

@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(student_id: str, session: AsyncSession = Depends(get_session)):
    """Get student by ID."""
    query = select(Student).where(Student.student_id == student_id)
    result = await session.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentSchema.from_orm(student)

@router.post("/", response_model=StudentSchema)
async def create_student(
    student: StudentSchema,
    session: AsyncSession = Depends(get_session)
):
    """Create new student."""
    # Verify class exists
    class_query = select(Class).where(Class.class_code == student.primary_class)
    class_result = await session.execute(class_query)
    if not class_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if student already exists
    existing = select(Student).where(Student.student_id == student.student_id)
    if await session.execute(existing):
        raise HTTPException(status_code=400, detail="Student already exists")

    new_student = Student(
        student_id=student.student_id,
        name=student.name,
        primary_class=student.primary_class
    )
    session.add(new_student)
    await session.commit()
    await session.refresh(new_student)

    return StudentSchema.from_orm(new_student)

@router.put("/{student_id}", response_model=StudentSchema)
async def update_student(
    student_id: str,
    student: StudentSchema,
    session: AsyncSession = Depends(get_session)
):
    """Update student."""
    query = select(Student).where(Student.student_id == student_id)
    result = await session.execute(query)
    db_student = result.scalar_one_or_none()

    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify class exists
    class_query = select(Class).where(Class.class_code == student.primary_class)
    class_result = await session.execute(class_query)
    if not class_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Class not found")

    db_student.name = student.name
    db_student.primary_class = student.primary_class

    await session.commit()
    await session.refresh(db_student)

    return StudentSchema.from_orm(db_student)

@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete student."""
    query = select(Student).where(Student.student_id == student_id)
    result = await session.execute(query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    await session.delete(student)
    await session.commit()

    return {"message": "Student deleted successfully"}

@router.post("/bulk-import")
async def bulk_import_students(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """Bulk import students from CSV."""
    content = await file.read()
    text = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = []

    for row in csv_reader:
        try:
            if not all(k in row for k in ['student_id', 'name', 'primary_class']):
                errors.append("CSV missing required columns: student_id, name, primary_class")
                continue

            # Verify class exists
            class_query = select(Class).where(Class.class_code == row['primary_class'])
            class_result = await session.execute(class_query)
            if not class_result.scalar_one_or_none():
                errors.append(f"Class {row['primary_class']} not found for student {row['student_id']}")
                continue

            # Check if student exists
            existing = select(Student).where(Student.student_id == row['student_id'])
            if await session.execute(existing):
                errors.append(f"Student {row['student_id']} already exists")
                continue

            student = Student(
                student_id=row['student_id'],
                name=row['name'],
                primary_class=row['primary_class']
            )
            session.add(student)
            imported += 1
        except Exception as e:
            errors.append(f"Error processing row {row}: {str(e)}")

    await session.commit()

    return {
        "imported": imported,
        "errors": errors,
        "total_errors": len(errors)
    }
