from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.enums import ResultTypeEnum

class ResultBase(BaseModel):
    result_name: Optional[str] = None
    type:  Optional[str] = ResultTypeEnum.custom
    confidence: Optional[List[float]] = None
    labels: Optional[List[int]] = None
    last_view_at: Optional[datetime] = datetime.utcnow()
    last_edited_at: Optional[datetime] = datetime.utcnow()
    created_at: Optional[datetime] = datetime.utcnow()
    study_id: int

class ResultCreate(ResultBase):
    pass

class ResultUpdate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    xray_path: Optional[str] = None
    region_path: Optional[str]  = None
    heatmap_path: Optional[str] = None
    report_path: Optional[str] = None
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class ResultShow(Result):
    pass
