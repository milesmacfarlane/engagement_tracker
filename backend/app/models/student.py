"""Student model."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    primary_class = Column(String(50), ForeignKey("classes.class_code"), nullable=False)

    # Relationships
    class_obj = relationship("Class", back_populates="students")
    observations = relationship("Observation", back_populates="student")
