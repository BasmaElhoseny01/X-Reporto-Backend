from sqlalchemy.orm import Session
from fastapi import HTTPException,status, UploadFile
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

        result.last_edited_at = datetime.utcnow()
        result.last_view_at = datetime.utcnow()
        
        return self.result_repo.update(result)
        
    def show(self,id:int) ->  Optional[Result]:
        return self.result_repo.show(id)
    
    def get_result_by_study_type(self,study_id: int, type: ResultTypeEnum) -> Optional[Result]:

        result = self.result_repo.get_result_by_study_type(study_id,type)
        if not result:
            return None
        return result
    
    def run_heatmap(self , result_id: int, xray_path: str) -> Result:
            
            # send the xray image to the AI model
            url = configs.AI_MODEL_URL+"/heatmap/generate_heatmap"
    
            files = {'image': open(xray_path, 'rb')}
    
            try:
                response = requests.post(url, files=files, timeout=60)
    
                print(response.status_code)
    
                # if successful, save the heatmap
                if response.status_code == 200:
    
                    response = response.json()
                    heatmap = response["heatmap"] # numpy array of shape(8.7,7)
                    labels = response["labels"] 
                    confidence = response["confidence"]
                    severity = response["severity"]
                    report = response["report"]
    
                    # save the heatmap of shape (8.7,7) as an image
                    heatmap_path = f"static/heatmaps/{result_id}_heatmap.png"
                    os.makedirs(os.path.dirname(heatmap_path), exist_ok=True)
                    cv2.imwrite(heatmap_path, heatmap)

                    # save the report
                    report_path = f"static/reports/{result_id}_report.txt"
                    os.makedirs(os.path.dirname(report_path), exist_ok=True)
                    with open(report_path, "w") as f:
                        f.write(report)
    
                    # save the labels and confidence
                    result = self.result_repo.show(result_id)
                    result.confidence = confidence
                    result.labels = labels
                    result.heatmap_path = heatmap_path
                    result.report_path = report_path
                    result.last_edited_at = datetime.utcnow()
                    result.last_view_at = datetime.utcnow()
    
                    # save severity in study of the result
                    study = self.study_repo.show(result.study_id)
                    study.severity = severity
                    self.study_repo.update(study)
                    self.result_repo.update(result)
                    print("Heatmap saved")
            except Exception as e:
                print(e)
                # delete the result
                self.result_repo.destroy(result_id)

    def run_llm(self , result_id: int, xray_path: str) -> Result:

        # send the xray image to the AI model
        url = configs.AI_MODEL_URL+"/x_reporto/report"

        files = {'image': open(xray_path, 'rb')}


        try:

            response = requests.post(url, files=files, timeout=60)

            print(response.status_code)

            # if successful, save the report and heatmap
            if response.status_code == 200:

                response = response.json()
                bounding_boxes = response["bounding_boxes"]
                report_text = response["report_text"]
                class_labels = response["detected_classes"]


                # save the report
                report_path = f"static/reports/{result_id}_report.txt"
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                with open(report_path, "w") as f:
                    f.write(report_text)

                # save bounding boxes array of arrays of floats in region_path along with class labels in correct format that can be read in two arrays
                region_path = f"static/regions/{result_id}_region.txt"
                os.makedirs(os.path.dirname(region_path), exist_ok=True)
                with open(region_path, "w") as f:
                    for i, box in enumerate(bounding_boxes):
                        f.write(f"{class_labels[i]} {box[0]} {box[1]} {box[2] - box[0]} {box[3] - box[1]}\n")
                
                # fetch the result
                result = self.result_repo.show(result_id)
                # save path to report and region
                result.report_path = report_path
                result.region_path = region_path
                result.last_edited_at = datetime.utcnow()
                result.last_view_at = datetime.utcnow()

                # save in the database
                self.result_repo.update(result)

                print("Report saved")
        except Exception as e:
            print(e)
            # delete the result
            self.result_repo.destroy(result_id)
    
    def upload_report(self,result: Result, report: UploadFile) -> Result:
        # save the report
        report_path = f"static/reports/{result.id}_report.txt"
        with open(report_path, "wb") as f:
            f.write(report.file.read())
        
        result.report_path = report_path
        result.last_edited_at = datetime.utcnow()
        result.last_view_at = datetime.utcnow()
        return self.result_repo.update(result)
        