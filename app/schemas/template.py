from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TemplateBase(BaseModel):
    template_name: Optional[str] = None
    template_path: Optional[str] = None
    doctor_id: Optional[int] = None
    last_view_at: Optional[datetime] = datetime.utcnow()
    last_edited_at: Optional[datetime] = datetime.utcnow()

class TemplateCreate(TemplateBase):
    created_at: Optional[datetime] = datetime.utcnow()

class TemplateUpdate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int
    used_count: Optional[int] = 0
    created_at: Optional[datetime] = datetime.utcnow()

    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True