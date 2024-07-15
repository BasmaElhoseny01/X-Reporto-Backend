from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.patient import PatientRepository
from app.models.patient import Patient
from app.models.enums import StatusEnum
from typing import List, Optional



class PatientService:
    """
    Service layer for managing Patient operations, handling business logic
    and interacting with the Patient repository.

    Attributes:
        patient_repo (PatientRepository): Repository for patient operations.
    """
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo
    
    def get_all(self) -> List[Patient]:
        """
        Retrieve all patients.

        Returns:
            List[Patient]: A list of all patients.
        """
        return self.patient_repo.get_all()
    
    def create(self,patient: dict) -> Patient:
        """
        Create a new patient and persist it to the database.

        Args:
            patient (dict): The patient data to create.

        Returns:
            Patient: The created patient object.
        """
        # create a new patient
        patient = Patient(**patient)
        return self.patient_repo.create(patient)
    
    def destroy(self,id:int) -> bool:
        """
        Delete a patient by its ID.

        Args:
            id (int): The ID of the patient to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        return self.patient_repo.destroy(id)
    
    def update(self,id:int,patient_data:dict) -> Patient:
        """
        Update an existing patient.

        Args:
            id (int): The ID of the patient to update.
            patient_data (dict): The data to update the patient with.

        Returns:
            Patient: The updated patient object.

        Raises:
            HTTPException: If the patient is not found.
        """
        patient = self.patient_repo.show(id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Patient with id {id} not found")
        # update the patient
        for key, value in patient_data.items():
            setattr(patient,key,value)
            
        self.patient_repo.update(patient)
        return patient
    
    def show(self,id:int) -> Optional[Patient]:
        """
        Retrieve a single patient by its ID.

        Args:
            id (int): The ID of the patient to retrieve.

        Returns:
            Optional[Patient]: The retrieved patient object, or None if not found.
        """
        return self.patient_repo.show(id)
    
    def show_with_studies(self,id:int,status: StatusEnum, limit: int, skip: int, sort: str) -> Optional[Patient]:
        """
        Retrieve a patient along with their associated studies.

        Args:
            id (int): The ID of the patient to retrieve.
            status (StatusEnum): The status of the studies to filter.
            limit (int): The number of studies to retrieve.
            skip (int): The number of studies to skip for pagination.
            sort (str): The sorting order for the studies.

        Returns:
            Optional[Patient]: The retrieved patient object with studies, or None if not found.
        """
        return self.patient_repo.show_with_studies(id,status, limit, skip, sort)