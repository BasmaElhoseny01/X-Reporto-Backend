import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from app.middleware.authentication import security
from app.models import patient, employee, doctor, study, result, template
from app.routers.v1 import patient, employee, authentication, doctor, template, study
from app.models.database import engine, Base, create_database_if_not_exists



create_database_if_not_exists()
# Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

prefix = "/api/v1"
app.include_router(authentication.router, prefix= prefix)
app.include_router(patient.router, prefix= prefix)
app.include_router(employee.router, prefix= prefix)
app.include_router(doctor.router, prefix= prefix)
app.include_router(template.router, prefix= prefix)
app.include_router(study.router, prefix= prefix)


@app.get("/")
async def index():
    return "Welcome to the X-Reporto API"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
'''
Now, you can run the application using the following command:
python app/main.py
'''