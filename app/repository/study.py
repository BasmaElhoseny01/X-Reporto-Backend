from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException,status
from app.models.study import Study
from app.models.patient import Patient
from app.models.enums import StatusEnum
from typing import List, Optional


class StudyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, status: StatusEnum, limit: int, skip: int, sort: str ) -> List[Study]:
        # get all studies non deleted or archived
        query = self.db.query(Study)

        if status:
            # filter by status and is_deleted
            query = query.filter(Study.status == status, Study.is_deleted == False)
        else:
            # filter by is_deleted
            query = query.filter(Study.is_deleted == False)
    
        if sort:
            sort_key = sort.lstrip("-")
            if sort.startswith("-"):
                query = query.order_by(getattr(Study,sort_key).desc())
            else:
                query = query.order_by(getattr(Study,sort_key).asc())

        studies = query.limit(limit).offset(skip).all()
        return studies
    
    def create(self,study: Study) -> Study:
        self.db.add(study)
        self.db.commit()
        self.db.refresh(study)
        return study
    
    def destroy(self,id:int) -> bool:
        study = self.db.query(Study).filter(Study.id == id)
        if not study.first():
            return False

        study.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,study:Study) -> Study:
        self.db.commit()
        self.db.refresh(study)
        return study
    
    
    def show(self,id:int) ->  Optional[Study]:
        # populate the patient
        study = self.db.query(Study).filter(Study.id == id).first()
        if not study:
            return None
        
        # request the patient to be loaded
        patient = self.db.query(Patient).filter(Patient.id == study.patient_id).first()

        # assign the patient to the study
        study.patient = patient
        return study
    
    def get_patient_studies(self,patient_id:int,status: StatusEnum, limit: int, skip: int, sort: str) -> List[Study]:
        query = self.db.query(Study).filter(Study.patient_id == patient_id, Study.is_deleted == False, Study.status != StatusEnum.archived)
        if sort:
            sort_key = sort.lstrip("-")
            if sort.startswith("-"):
                query = query.order_by(getattr(Study,sort_key).desc())
            else:
                query = query.order_by(getattr(Study,sort_key).asc())
        
        if status:
            query = query.filter(Study.status == status)
        studies = query.limit(limit).offset(skip).all()
        return studies
    
    def archive(self,id:int, doctor_id: int) -> bool:
        study = self.db.query(Study).filter(Study.id == id)
        if not study.first():
            return False , "Study not found"
        
        if study.first().doctor_id != doctor_id:
            return False , "You are not allowed to archive this study"
        
        # check if the study is already archived
        if study.first().status == StatusEnum.archived:
            return False , "Study already archived"
        
        study.update({"status":StatusEnum.archived})
        self.db.commit()
        return True , "Study archived successfully"
    
    def unarchive(self,id:int, doctor_id) -> bool:
        study = self.db.query(Study).filter(Study.id == id)
        if not study.first():
            return False , "Study not found"
        
        if study.first().doctor_id != doctor_id:
            return False , "You are not allowed to unarchive this study"
        
        # check if the study is already unarchived
        if not study.first().status == StatusEnum.archived:
            return False , "Study already unarchived"
        
        study.update({"status":StatusEnum.new})
        self.db.commit()
        return True , "Study unarchived successfully"

    def assign_doctor(self,study_id:int, doctor_id:int) -> bool:
        study = self.db.query(Study).filter(Study.id == study_id)
        if not study.first():
            return False, "Study not found"
        
        # check if the doctor is already assigned
        if study.first().doctor_id:
            if study.first().doctor_id == doctor_id:
                return False, "You are already assigned to study"
            else:
                return False, "Doctor already assigned to study"
        
        study.update({"doctor_id":doctor_id, "status":StatusEnum.in_progress})
        self.db.commit()
        return True, "Doctor assigned successfully"
    
    def unassign_doctor(self,study_id:int, doctor_id: int) -> bool:
        study = self.db.query(Study).filter(Study.id == study_id)
        if not study.first():
            return False, "Study not found"
        
        if study.first().doctor_id != doctor_id:
            return False, "You are not allowed to unassign this study"
        
        if study.first().status == StatusEnum.completed:
            return False, "Study already completed"
        
        study.update({"doctor_id":None, "status":StatusEnum.new})
        self.db.commit()
        return True, "Doctor unassigned successfully"
    
    def get_assigned_studies(self,employee_id: int, status: StatusEnum, limit: int, skip: int, sort: str) -> List[Study]:

        query = self.db.query(Study).filter(Study.doctor_id == employee_id, Study.is_deleted == False)
        if status:
            query = query.filter(Study.status == status)

        if sort:
            sort_key = sort.lstrip("-")
            if sort.startswith("-"):
                query = query.order_by(getattr(Study,sort_key).desc())
            else:
                query = query.order_by(getattr(Study,sort_key).asc())

        studies = query.limit(limit).offset(skip).all()
        # studies = self.db.query(Study).filter(Study.doctor_id == employee_id, Study.status.in_([StatusEnum.completed,StatusEnum.in_progress])).all()
        return studies

    def get_new_studies_count(self):
        return self.db.query(Study).filter(Study.status == StatusEnum.new).count()
    
    def get_incomplete_studies_count(self):
        # get new and in progress studies
        return self.db.query(Study).filter(Study.status == StatusEnum.in_progress).count()
        

    def get_pending_studies_count(self,doctor_id:int):
        return self.db.query(Study).filter(Study.doctor_id == doctor_id, Study.status == StatusEnum.in_progress).count()
        
    
    def get_completed_studies_count(self,doctor_id:int):
        return self.db.query(Study).filter(Study.doctor_id == doctor_id, Study.status == StatusEnum.completed).count()
