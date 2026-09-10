"""Class management routes."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from pydantic import BaseModel

from app.database import get_session
from app.models import Class, Student

router = APIRouter()

class ClassSchema(BaseModel):
    class_code: str
    class_name: str

    class Config:
        from_attributes = True

class ClassDetailSchema(ClassSchema):
    student_count: int = 0

@router.get("/", response_model=list[ClassSchema])
async def list_classes(session: AsyncSession = Depends(get_session)):
    """List all classes."""
    query = select(Class)
    result = await session.execute(query)
    classes = result.scalars().all()

    return [ClassSchema.from_orm(c) for c in classes]

@router.get("/{class_code}", response_model=ClassDetailSchema)
async def get_class(class_code: str, session: AsyncSession = Depends(get_session)):
    """Get class by code with student count."""
    query = select(Class).where(Class.class_code == class_code)
    result = await session.execute(query)
    class_obj = result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Count students in class
    student_count_query = select(Student).where(Student.primary_class == class_code)
    student_result = await session.execute(student_count_query)
    student_count = len(student_result.scalars().all())

    return {
        "class_code": class_obj.class_code,
        "class_name": class_obj.class_name,
        "student_count": student_count
    }

@router.post("/", response_model=ClassSchema)
async def create_class(
    class_obj: ClassSchema,
    session: AsyncSession = Depends(get_session)
):
    """Create new class."""
    # Check if class already exists
    existing = select(Class).where(Class.class_code == class_obj.class_code)
    if await session.execute(existing):
        raise HTTPException(status_code=400, detail="Class already exists")

    new_class = Class(
        class_code=class_obj.class_code,
        class_name=class_obj.class_name
    )
    session.add(new_class)
    await session.commit()
    await session.refresh(new_class)

    return ClassSchema.from_orm(new_class)

@router.put("/{class_code}", response_model=ClassSchema)
async def update_class(
    class_code: str,
    class_obj: ClassSchema,
    session: AsyncSession = Depends(get_session)
):
    """Update class."""
    query = select(Class).where(Class.class_code == class_code)
    result = await session.execute(query)
    db_class = result.scalar_one_or_none()

    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    db_class.class_name = class_obj.class_name

    await session.commit()
    await session.refresh(db_class)

    return ClassSchema.from_orm(db_class)

@router.delete("/{class_code}")
async def delete_class(
    class_code: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete class (only if no students)."""
    # Check if class has students
    student_query = select(Student).where(Student.primary_class == class_code)
    student_result = await session.execute(student_query)
    students = student_result.scalars().all()

    if students:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete class with {len(students)} students. Remove students first."
        )

    query = select(Class).where(Class.class_code == class_code)
    result = await session.execute(query)
    class_obj = result.scalar_one_or_none()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    await session.delete(class_obj)
    await session.commit()

    return {"message": "Class deleted successfully"}
