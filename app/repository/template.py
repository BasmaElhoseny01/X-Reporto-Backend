from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.template import Template
from typing import List, Optional


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Template]:
        templates = self.db.query(Template).all()
        return templates
    
    def create(self,template: Template) -> Template:
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def destroy(self,id:int) -> bool:
        template = self.db.query(Template).filter(Template.id == id)
        if not template.first():
            return False

        template.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,template:Template) -> Template:
        self.db.commit()
        self.db.refresh(template)
        return template
    
    
    def show(self,id:int) ->  Optional[Template]:
        template = self.db.query(Template).filter(Template.id == id).first()
        if not template:
            return None
        return template

