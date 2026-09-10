"""Class model."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class Class(Base):
    __tablename__ = "classes"

    class_code = Column(String(50), primary_key=True)
    class_name = Column(String(255), nullable=False)

    # Relationships
    students = relationship("Student", back_populates="class_obj")
    observations = relationship("Observation", back_populates="class_obj")
