"""Observation model."""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    class_code = Column(String(50), ForeignKey("classes.class_code"), nullable=False)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False)
    measure_name = Column(String(255), nullable=False)
    value = Column(String(10), nullable=False)  # "1", "0", or "-"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    class_obj = relationship("Class", back_populates="observations")
    student = relationship("Student", back_populates="observations")

    # Indexes for performance
    __table_args__ = (
        Index('idx_obs_student_date', 'student_id', 'date'),
        Index('idx_obs_class_date', 'class_code', 'date'),
        Index('idx_obs_date', 'date'),
    )
