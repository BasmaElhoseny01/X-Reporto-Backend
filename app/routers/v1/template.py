from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile
from app.models import database
from app.schemas import template as template_schema, authentication as auth_schema
from app.services.template import TemplateService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_template_service
from app.middleware.authentication import get_current_user, security
from fastapi.responses import FileResponse


# Create a new APIRouter instance
router = APIRouter(
    tags=["Templates"],
    prefix="/templates",
)

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)])
async def read_templates(limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service) ) -> List[template_schema.Template]:
    """
    Retrieve a list of templates with optional pagination and sorting.

    Args:
        limit (int): Maximum number of templates to return (default is 10).
        skip (int): Number of templates to skip (default is 0).
        sort (str): Sorting criteria for templates.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        List[template_schema.Template]: A list of templates.
    """
    templates = template_service.get_all()
    return templates

# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)])
async def create_templates(request: template_schema.TemplateCreate,user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> template_schema.Template:
    """
    Create a new template.

    Args:
        request (template_schema.TemplateCreate): Template creation request body.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        template_schema.Template: The created template.
    """
    template = template_service.create(request.dict())
    return template

# Define a route for getting a single employee
@router.get("/{template_id}", dependencies=[Security(security)])
async def read_template(template_id: int,user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> template_schema.Template:
    """
    Retrieve a template by its ID.

    Args:
        template_id (int): The ID of the template to retrieve.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        template_schema.Template: The retrieved template.

    Raises:
        HTTPException: If the template is not found.
    """
    template = template_service.show(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template with id {template_id} not found")
    return template

# Define a route for updating an employee
@router.put("/{template_id}", dependencies=[Security(security)])
async def update_template(template_id: int, request: template_schema.TemplateUpdate,user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> template_schema.Template:
    """
    Update an existing template by its ID.

    Args:
        template_id (int): The ID of the template to update.
        request (template_schema.TemplateUpdate): Template update request body.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        template_schema.Template: The updated template.
    """
    template = template_service.update(template_id, request.dict())
    return template

# Define a route for deleting an employee
@router.delete("/{template_id}", dependencies=[Security(security)])
async def delete_template(template_id: int,user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> bool:
    """
    Delete a template by its ID.

    Args:
        template_id (int): The ID of the template to delete.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        bool: True if the template was successfully deleted.

    Raises:
        HTTPException: If the template is not found.
    """
    deleted = template_service.destroy(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Template with id {template_id} not found")
    return deleted

@router.post("/{template_id}/upload_template", dependencies=[Security(security)])
async def upload_template(template_id: int, file: UploadFile = File(...), user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> template_schema.Template:
    """
    Upload a new template file for a specific template ID.

    Args:
        template_id (int): The ID of the template to which the file belongs.
        file (UploadFile): The template file to upload.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        template_schema.Template: The updated template with the uploaded file.

    Raises:
        HTTPException: If the template is not found.
    """
    template = template_service.show(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template with id {template_id} not found")
    return template_service.upload_template(template, file)

# return actual file
@router.get("/{template_id}/download_template", dependencies=[Security(security)])
async def download_template(template_id: int, user: auth_schema.TokenData  = Depends(get_current_user), template_service: TemplateService = Depends(get_template_service)) -> FileResponse:
    """
    Download a specific template file by its ID.

    Args:
        template_id (int): The ID of the template to download.
        user (auth_schema.TokenData): Current authenticated user.
        template_service (TemplateService): Dependency for template operations.

    Returns:
        FileResponse: The requested template file.

    Raises:
        HTTPException: If the template is not found.
    """
    template = template_service.show(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template with id {template_id} not found")
    return template_service.download_template(template)