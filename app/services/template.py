from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.template import TemplateRepository
from app.models.template import Template
from typing import List, Optional



class TemplateService:
    def __init__(self, template_repo: TemplateRepository):
        self.template_repo = template_repo
    
    def get_all(self) -> List[Template]:
        return self.template_repo.get_all()
    
    def create(self,template: dict) -> Template:
        # create a new patient
        template = Template(**template)
        return self.template_repo.create(template)
    
    def destroy(self,id:int) -> bool:
        return self.template_repo.destroy(id)
    
    def update(self,id:int,template_data:dict) -> Template:
        template = self.template_repo.show(id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Template with id {id} not found")
        
        for key, value in template_data.items():
            setattr(template,key,value)
            
        self.template_repo.update(template)
        return template
    
    def show(self,id:int) -> Optional[Template]:
        return self.template_repo.show(id)
