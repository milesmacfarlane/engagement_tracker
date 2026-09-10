"""Class management routes."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_session

router = APIRouter()

class ClassSchema(BaseModel):
    class_code: str
    class_name: str

    class Config:
        from_attributes = True

@router.get("/", response_model=list[ClassSchema])
async def list_classes(session: AsyncSession = Depends(get_session)):
    """List all classes."""
    # TODO: Implement
    return []

@router.get("/{class_code}", response_model=ClassSchema)
async def get_class(class_code: str, session: AsyncSession = Depends(get_session)):
    """Get class by code."""
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Class not found")

@router.post("/", response_model=ClassSchema)
async def create_class(class_obj: ClassSchema, session: AsyncSession = Depends(get_session)):
    """Create new class."""
    # TODO: Implement
    return class_obj

@router.put("/{class_code}", response_model=ClassSchema)
async def update_class(class_code: str, class_obj: ClassSchema, session: AsyncSession = Depends(get_session)):
    """Update class."""
    # TODO: Implement
    return class_obj

@router.delete("/{class_code}")
async def delete_class(class_code: str, session: AsyncSession = Depends(get_session)):
    """Delete class."""
    # TODO: Implement
    return {"message": "Class deleted"}
