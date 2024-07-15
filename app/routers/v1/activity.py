from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.models.enums import ActivityEnum
from app.schemas import activity as activity_schema, authentication as auth_schema
from app.services.activity import ActivityService 
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_activity_service
from app.middleware.authentication import get_current_user, security

# Create a new APIRouter instance
router = APIRouter(
    tags=["Activities"],
    prefix="/activities",
)

# Define a route for the patient list
@router.get("/", dependencies=[Security(security)],
            response_model=List[activity_schema.Activity])
async def read_activities(activity_type: ActivityEnum = None, limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), activity_Service: ActivityService = Depends(get_activity_service) ) -> List[activity_schema.Activity]:
    """
    Retrieve a list of activities, restricted to doctors only.

    Args:
        activity_type (ActivityEnum): Optional filter for activity type.
        limit (int): Maximum number of activities to return (default is 10).
        skip (int): Number of activities to skip (default is 0).
        sort (str): Sorting criteria for activities.
        user (auth_schema.TokenData): Current authenticated user.
        activity_service (ActivityService): Dependency for activity operations.

    Returns:
        List[activity_schema.Activity]: A list of activities.

    Raises:
        HTTPException: If the user is not authorized (not a doctor).
    """
    # check if user is not a doctor
    if user.type != "doctor":
        # raise error
        raise HTTPException(status_code=401, detail="Unauthorized, only doctors can view activities")
    activities = activity_Service.get_all(user.id,activity_type, limit, skip, sort)
    return activities

# Define a route for creating a new patient
@router.post("/", dependencies=[Security(security)])
async def create_activity(request: activity_schema.ActivityCreate, user: auth_schema.TokenData  = Depends(get_current_user), activity_Service: ActivityService = Depends(get_activity_service)) -> activity_schema.Activity:
    """
    Create a new activity.

    Args:
        request (activity_schema.ActivityCreate): Activity creation request body.
        user (auth_schema.TokenData): Current authenticated user.
        activity_service (ActivityService): Dependency for activity operations.

    Returns:
        activity_schema.Activity: The created activity.
    """
    request.employee_id = user.id
    activity = activity_Service.create(request.dict())
    return activity

# Define a route for retrieving a patient by ID
@router.get("/{id}", dependencies=[Security(security)])
async def read_activity(id: int,user: auth_schema.TokenData  = Depends(get_current_user), activity_Service: ActivityService = Depends(get_activity_service)) -> activity_schema.Activity:
    """
    Retrieve an activity by its ID.

    Args:
        id (int): The ID of the activity to retrieve.
        user (auth_schema.TokenData): Current authenticated user.
        activity_service (ActivityService): Dependency for activity operations.

    Returns:
        activity_schema.Activity: The retrieved activity.

    Raises:
        HTTPException: If the activity is not found.
    """
    activity = activity_Service.show(id)
    if not activity:
        raise HTTPException(status_code=404, detail=f"Activity with id {id} not found")
    return activity

# Define a route for updating a patient by ID
@router.put("/{id}", dependencies=[Security(security)] )
async def update_activity(id: int, request: activity_schema.ActivityCreate,user: auth_schema.TokenData  = Depends(get_current_user), activity_Service: ActivityService = Depends(get_activity_service)) -> activity_schema.Activity:
    """
    Update an existing activity by its ID.

    Args:
        id (int): The ID of the activity to update.
        request (activity_schema.ActivityCreate): Activity update request body.
        user (auth_schema.TokenData): Current authenticated user.
        activity_service (ActivityService): Dependency for activity operations.

    Returns:
        activity_schema.Activity: The updated activity.
    """
    activity = activity_Service.update(id, request.dict())
    return activity

# Define a route for deleting a patient by ID
@router.delete("/{id}", dependencies=[Security(security)])
async def delete_activity(id: int,user: auth_schema.TokenData  = Depends(get_current_user), activity_Service: ActivityService = Depends(get_activity_service)) -> bool:
    """
    Delete an activity by its ID.

    Args:
        id (int): The ID of the activity to delete.
        user (auth_schema.TokenData): Current authenticated user.
        activity_service (ActivityService): Dependency for activity operations.

    Returns:
        bool: True if the activity was successfully deleted.

    Raises:
        HTTPException: If the activity is not found.
    """
    result = activity_Service.destroy(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Activity with id {id} not found")
    return result


