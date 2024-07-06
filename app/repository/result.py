from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException,status
from app.models.result import Result
from app.models.patient import Patient
from app.models.enums import ResultTypeEnum
from app.models.database import get_db
from typing import List, Optional
from datetime import datetime


class ResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, type: ResultTypeEnum, limit: int, skip: int, sort: str ) -> List[Result]:
        # get all studies non deleted or archived
        query = self.db.query(Result)

        if type:
            # filter by status and is_deleted
            query = query.filter(Result.type == type)
    
        if sort:
            sort_key = sort.lstrip("-")
            if sort.startswith("-"):
                query = query.order_by(getattr(Result,sort_key).desc())
            else:
                query = query.order_by(getattr(Result,sort_key).asc())

        studies = query.limit(limit).offset(skip).all()
        return studies
    
    def create(self,result: Result) -> Result:
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
    
    def destroy(self,id:int) -> bool:
        result = self.db.query(Result).filter(Result.id == id)
        if not result.first():
            return False

        result.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,result:Result) -> Result:
        # db.merge(result)
        self.db.commit()
        self.db.refresh(result)
        return result
    
    
    def show(self,id:int) ->  Optional[Result]:
        # populate the patient
        result = self.db.query(Result).filter(Result.id == id).first()
        if not result:
            return None
        
        # update the last_view_at
        result.last_view_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(result)
        return result
    
    def get_results_by_study(self,study_id:int) -> List[Result]:
        results = self.db.query(Result).filter(Result.study_id == study_id).all()
        return results
    
    def get_result_by_study_type(self,study_id: int, type: ResultTypeEnum) -> Result:
        print(study_id,type)
        result = self.db.query(Result).filter(Result.study_id == study_id, Result.type == type).first()
        return result
    
