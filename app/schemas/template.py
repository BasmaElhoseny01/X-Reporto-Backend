from pydantic import BaseModel
from typing import Optional
import datetime

class TemplateBase(BaseModel):
    template_name: Optional[str] = None
    template_path: Optional[str] = None
    doctor_id: Optional[int] = None
    last_view_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_edited_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TemplateCreate(TemplateBase):
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TemplateUpdate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int
    used_count: Optional[int] = 0
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True