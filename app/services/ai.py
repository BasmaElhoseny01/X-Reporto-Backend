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
import albumentations as A
import numpy as np



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
    
                    # save the heatmap of shape (8.7,7) in correct format
                    heatmap_path = f"static/heatmaps/{result_id}_heatmap"
                    os.makedirs(os.path.dirname(heatmap_path), exist_ok=True)
                    np.save(heatmap_path, heatmap)

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

    def denoise(self, result_id: int, xray_path: str) -> Result:
        # send the xray image to the AI model
        url = configs.AI_MODEL_URL+"/x_reporto/denoise"

        files = {'image': open(xray_path, 'rb')}

        try:
            response = requests.post(url, files=files, timeout=60)

            print(response.status_code)

            # if successful, save the heatmap
            if response.status_code == 200:
                
                # response is file like object
                response = response.content
                nparr = np.frombuffer(response, np.uint8)
                denoised_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # save the heatmap of shape (8.7,7) as an image
                denoised_path = f"static/denoised/{result_id}_denoised.png"
                os.makedirs(os.path.dirname(denoised_path), exist_ok=True)
                cv2.imwrite(denoised_path, denoised_image)

                # save the labels and confidence
                result = self.result_repo.show(result_id)
                result.xray_path = denoised_path
                result.last_edited_at = datetime.utcnow()
                result.last_view_at = datetime.utcnow()

                self.result_repo.update(result)
                print("Denoised image saved")
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
    
    def project_heatmap(self,image,heat_map):
        '''
        Overlays a heatmap [] onto an image.

        Parameters:
        - image: numpy.ndarray
            Original BGR image of shape (2544, 3056, 3) with pixel values in the range [0, 255].
        - heatmap: numpy.ndarray
            Heatmap of shape (7, 7) with normalized values in the range [0, 1].

        Returns:
        - image_resized: numpy.ndarray
            The original image resized to (224, 224, 3) in BGR format.
        - heatmap_resized: numpy.ndarray
            The heatmap resized to (224, 224, 3) in BGR format.
        - blended_image: numpy.ndarray
            The blended image of size (224, 224, 3) in BGR format, which is a weighted sum of the resized image and the heatmap.
        '''
        resize_and_pad_transform = A.Compose([
            A.LongestMaxSize(max_size=224, interpolation=cv2.INTER_AREA),
            A.PadIfNeeded(min_height=224, min_width=224, border_mode=cv2.BORDER_CONSTANT, value=0)
        ])

        # Resize Image to be HEAT_MAP_IMAGE_SIZExHEAT_MAP_IMAGE_SIZEx3 (224x224x3)
        # image_resized = cv2.resize(image, (HEAT_MAP_IMAGE_SIZE, HEAT_MAP_IMAGE_SIZE)) #(224, 224, 3)
        image_resized = resize_and_pad_transform(image=image)["image"]

        # Resize Heat Map to be same size as the image (224x224x3)
        heatmap_resized = cv2.resize(heat_map, (224, 224))

        # Define Color Map [generates a heatmap image from the input cam data, where different intensity values in cam are mapped to corresponding colors in the "jet" colormap.]
        heatmap_resized=cv2.applyColorMap(np.uint8(255*heatmap_resized), cv2.COLORMAP_JET) 


        print(heatmap_resized.shape)
        print(image_resized.shape)
        # Weighted Sum 1*img + 0.25*heatmap (224x224x3)
        blended_image = cv2.addWeighted(image_resized,1,heatmap_resized,0.35,0)

        # cv2.imwrite('./img.png',image_resized)
        # cv2.imwrite('./heat.png',heatmap_resized)
        # cv2.imwrite('./blend.png',blended_image)

        return image_resized,heatmap_resized,blended_image

    def get_heatmap(self,result_id: int, label: int) -> np.ndarray:
        # get the result
        result = self.result_repo.show(result_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Result not found")
        
        # check if the heatmap exists
        if not result.heatmap_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Heatmap not found")
        
        # load the heatmap
        heatmap = np.load(result.heatmap_path+".npy")

        # load image
        xray = cv2.imread(result.xray_path, cv2.IMREAD_COLOR)

        # project the heatmap on the xray
        _, _, blended_image = self.project_heatmap(xray, heatmap[label])

        #save the blended image
        blended_path = f"static/heatmaps/{result_id}_blended_{label}.png"
        cv2.imwrite(blended_path, blended_image)

        return blended_image

    
        
        