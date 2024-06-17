from pydantic import BaseModel
from typing import Optional
import datetime

class TemplateBase(BaseModel):
    template_name: Optional[str] = None
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template_path: Optional[str] = None
    used_count: Optional[int] = 0
    doctor_id: Optional[int] = None

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int
    
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True