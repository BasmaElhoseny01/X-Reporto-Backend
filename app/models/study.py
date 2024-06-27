from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import StatusEnum
import datetime


class Study(Base):
    __tablename__ = "studies"
    
    id = Column(Integer, primary_key=True, index=True)
    study_name = Column(String, index=True)
    notes = Column(String)
    status = Column(Enum(StatusEnum), default=StatusEnum.new)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.datetime.utcnow)
    severity = Column(Integer)
    xray_path = Column(String)
    xray_type = Column(String) # This should be an Enum
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    last_view_at = Column(DateTime, default = datetime.datetime.utcnow)
    last_edited_at = Column(DateTime, default = datetime.datetime.utcnow)
    # last_edited_by = Column(Integer, ForeignKey("doctors.id"))
    # last_viewed_by = Column(Integer, ForeignKey("doctors.id"))

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    patient = relationship("Patient", back_populates="studies", lazy="select")

    doctor_id = Column(Integer, ForeignKey("employees.id"))
    doctor = relationship("Employee", foreign_keys=[doctor_id], back_populates="assigned_studies",lazy='select')

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="studies",lazy='select')


    results = relationship("Result", back_populates="study", lazy="select")

    activities = relationship("Activity", back_populates="study",lazy='select')
    # doctor_last_edited = relationship("Doctor", foreign_keys=[last_edited_by])
    # doctor_last_viewed = relationship("Doctor", foreign_keys=[last_viewed_by])

    