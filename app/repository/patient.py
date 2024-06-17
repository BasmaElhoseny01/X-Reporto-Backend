from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.patient import Patient
from typing import List, Optional


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Patient]:
        patients = self.db.query(Patient).all()
        return patients
    
    def create(self,patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def destroy(self,id:int) -> bool:
        patient = self.db.query(Patient).filter(Patient.id == id)
        if not patient.first():
            return False

        patient.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,patient:Patient) -> Patient:
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    
    def show(self,id:int) ->  Optional[Patient]:
        patient = self.db.query(Patient).filter(Patient.id == id).first()
        if not patient:
            return None
        return patient
