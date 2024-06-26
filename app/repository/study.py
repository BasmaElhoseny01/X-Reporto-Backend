from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.study import Study
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
        study = self.db.query(Study).filter(Study.id == id).first()
        if not study:
            return None
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
        
        study.update({"is_archived":True})
        self.db.commit()
        return True , "Study archived successfully"
    
    def unarchive(self,id:int, doctor_id) -> bool:
        study = self.db.query(Study).filter(Study.id == id)
        if not study.first():
            return False , "Study not found"
        
        if study.first().doctor_id != doctor_id:
            return False , "You are not allowed to unarchive this study"
        
        study.update({"is_archived":False})
        self.db.commit()
        return True , "Study unarchived successfully"
