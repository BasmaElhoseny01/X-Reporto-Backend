from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.study import Study
from typing import List, Optional


class StudyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Study]:
        # get all studies non deleted or archived
        studies = self.db.query(Study).filter(Study.is_deleted == False, Study.is_archived == False).all()
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
