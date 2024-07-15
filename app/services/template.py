from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from app.repository.template import TemplateRepository
from app.models.template import Template
from typing import List, Optional
import datetime
import os


class TemplateService:
    """
    Service layer for managing Template operations, handling business logic
    and interacting with the Template repository.

    Attributes:
        template_repo (TemplateRepository): Repository for template operations.
    """
    def __init__(self, template_repo: TemplateRepository):
        self.template_repo = template_repo
    
    def get_all(self) -> List[Template]:
        """
        Retrieve all templates.

        Returns:
            List[Template]: A list of all templates.
        """
        return self.template_repo.get_all()
    
    def create(self,template: dict) -> Template:
        """
        Create a new template and persist it to the database.

        Args:
            template (dict): The template data to create.

        Returns:
            Template: The created template object.
        """
        # create a new patient
        template = Template(**template)
        return self.template_repo.create(template)
    
    def destroy(self,id:int) -> bool:
        """
        Delete a template by its ID.

        Args:
            id (int): The ID of the template to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        return self.template_repo.destroy(id)
    
    def update(self,id:int,template_data:dict) -> Template:
        """
        Update an existing template.

        Args:
            id (int): The ID of the template to update.
            template_data (dict): The data to update the template with.

        Returns:
            Template: The updated template object.

        Raises:
            HTTPException: If the template is not found.
        """
        template = self.template_repo.show(id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Template with id {id} not found")
        
        for key, value in template_data.items():
            setattr(template,key,value)
            
        self.template_repo.update(template)
        return template
    
    def show(self,id:int) -> Optional[Template]:
        """
        Retrieve a single template by its ID.

        Args:
            id (int): The ID of the template to retrieve.

        Returns:
            Optional[Template]: The retrieved template object, or None if not found.
        """
        return self.template_repo.show(id)

    def upload_template(self,template: Template,file) -> Template:
        """
        Upload a template file and save it to the filesystem.

        Args:
            template (Template): The template to upload the file for.
            file: The uploaded file containing the template.

        Returns:
            Template: The updated template object with the file path.

        Raises:
            HTTPException: If the upload fails.
        """
        # save the file to the file system and update the template file_path
        file_path = f"static/templates/{template.id}/{file.filename}"

        # create the file path and nested directories
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        template.template_path = file_path
        template.last_edited_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.template_repo.update(template)
        return template
    def download_template(self,template: Template) -> FileResponse:
        """
        Download the template file associated with a template.

        Args:
            template (Template): The template to download the file from.

        Returns:
            FileResponse: The response containing the template file.

        Raises:
            HTTPException: If the template file is not found.
        """
        if not template.template_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Template file not found")
        return FileResponse(template.template_path)