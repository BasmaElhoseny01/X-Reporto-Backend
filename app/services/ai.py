from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.study import StudyRepository
from app.repository.activity import ActivityRepository
from app.repository.result import ResultRepository
from app.models.study import Study
from app.models.activity import Activity
from app.models.result import Result
from app.models.enums import StatusEnum, ActivityEnum, ResultTypeEnum
from typing import List, Optional
from datetime import datetime
from app.core.config import configs
import os
import requests
import cv2


class AIService:
    def __init__(self, study_repo: StudyRepository, result_repo: ResultRepository, activity_repo: ActivityRepository):
        self.study_repo = study_repo
        self.activity_repo = activity_repo
        self.result_repo = result_repo
    
    def get_all(self,type: ResultTypeEnum , limit: int, skip: int , sort: str) -> List[Result]:
        return self.result_repo.get_all(type, limit, skip, sort)
    
    def create(self,result: dict) -> Result:
        # create a new study
        result = Result(**result)
        return self.result_repo.create(result)
    
    def destroy(self,id:int) -> bool:
        return self.result_repo.destroy(id)
    
    def update(self,id:int,result__data:dict) -> Result:
        result = self.result_repo.show(id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Result not found")
        
        for key, value in result__data.items():
            setattr(result, key, value)
        
        return self.result_repo.update(result)
        
    def show(self,id:int) ->  Optional[Result]:
        return self.result_repo.show(id)
    
    def get_result_by_study_type(self,study_id: int, type: ResultTypeEnum) -> Optional[Result]:

        result = self.result_repo.get_result_by_study_type(study_id,type)
        if not result:
            return None
        return result

    def run_llm(self , result_id: int, xray_path: str) -> Result:

        # send the xray image to the AI model
        url = configs.AI_MODEL_URL+"/x_reporto/report"

        files = {'image': open(xray_path, 'rb')}

        response = requests.post(url, files=files)

        print(response.status_code)

        # if successful, save the report and heatmap
        if response.status_code == 200:

            response = response.json()
            bounding_boxes = response["bounding_boxes"]
            report_text = response["report_text"]


            # save the report
            report_path = f"static/reports/{result_id}_report.txt"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w") as f:
                f.write(report_text)

            # save bounding boxes array of arrays of floats in region_path
            region_path = f"static/regions/{result_id}_region.txt"
            os.makedirs(os.path.dirname(region_path), exist_ok=True)
            with open(region_path, "w") as f:
                f.write(str(bounding_boxes))
            
            # fetch the result
            result = self.result_repo.show(result_id)
            # save path to report and region
            result.report_path = report_path
            result.region_path = region_path

            # save in the database
            self.result_repo.update(result)

            print("Report saved")
        