from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from app.repository.template import TemplateRepository
from app.models.template import Template
from typing import List, Optional
import datetime
import os


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

    def upload_template(self,template: Template,file) -> Template:
        # check if file is word or docx file
        if not file.content_type.startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid file type. Only word files are allowed")
        
        # save the file to the file system and update the template file_path
        file_path = f"static/templates/{template.id}/template.docx"

        # create the file path and nested directories
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        template.template_path = file_path
        template.last_edited_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.template_repo.update(template)
        return template
    def download_template(self,template: Template) -> FileResponse:
        if not template.template_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Template file not found")
        return FileResponse(template.template_path)