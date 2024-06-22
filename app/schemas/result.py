from pydantic import BaseModel
from typing import Optional
import datetime
from app.models.enums import ResultTypeEnum

class ResultBase(BaseModel):
    result_name: Optional[str] = None
    type:  Optional[str] = ResultTypeEnum.custom
    confidence: Optional[str] = None
    last_view_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_edited_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    region_path: Optional[str] 
    heatmap_path: Optional[str] = None
    report_path: Optional[str] = None
    study_id: int

class ResultCreate(ResultBase):
    pass

class ResultUpdate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class ResultShow(Result):
    pass
