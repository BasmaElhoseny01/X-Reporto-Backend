import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models import patient, employee, doctor, study, result, template
from app.routers.v1 import patient
from app.models.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(patient.router)

@app.get("/")
async def index():
    return "Welcome to the X-Reporto API"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
'''
Now, you can run the application using the following command:
python app/main.py
'''