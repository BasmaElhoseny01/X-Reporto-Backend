from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.patient import PatientRepository
from app.models.patient import Patient
from app.models.enums import StatusEnum
from typing import List, Optional



class PatientService:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo
    
    def get_all(self) -> List[Patient]:
        return self.patient_repo.get_all()
    
    def create(self,patient: dict) -> Patient:
        # create a new patient
        patient = Patient(**patient)
        return self.patient_repo.create(patient)
    
    def destroy(self,id:int) -> bool:
        return self.patient_repo.destroy(id)
    
    def update(self,id:int,patient_data:dict) -> Patient:
        patient = self.patient_repo.show(id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Patient with id {id} not found")
        # update the patient
        for key, value in patient_data.items():
            setattr(patient,key,value)
            
        self.patient_repo.update(patient)
        return patient
    
    def show(self,id:int) -> Optional[Patient]:
        return self.patient_repo.show(id)
    
    def show_with_studies(self,id:int,status: StatusEnum, limit: int, skip: int, sort: str) -> Optional[Patient]:
        return self.patient_repo.show_with_studies(id,status, limit, skip, sort)