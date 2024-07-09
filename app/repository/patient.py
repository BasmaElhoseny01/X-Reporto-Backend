from sqlalchemy.orm import Session, joinedload, contains_eager
from fastapi import HTTPException,status
from app.models.patient import Patient
from app.models.study import Study
from app.models.enums import StatusEnum
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
        # populate the studies
        
        return patient

    def show_with_studies(self,id:int,status: StatusEnum, limit: int, skip: int, sort: str) ->  Optional[Patient]:
        # query = self.db.query(Patient).filter(Patient.id == id).join(Patient.studies)
        query = self.db.query(Patient)
        query = query.join(Study, Patient.id == Study.patient_id).filter(Patient.id == id)
        if status:
            print(status)
            query = query.filter(Study.status == status)
        if sort:
            print(sort)
            sort_key = sort.lstrip("-")
            
            # sort by study attribute
            if sort.startswith("-"):
                print("descending")
                query = query.order_by(getattr(Study,sort_key).desc())
            else:
                query = query.order_by(getattr(Study,sort_key))



        print(query)

        patient = query.first()
        if not patient:
            return None
        
        if limit and skip:
            # limit and skip the results
            patient.studies = patient.studies[skip:skip+limit]

        return patient