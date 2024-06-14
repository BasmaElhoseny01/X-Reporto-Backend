import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models import patient
from app.models.database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def index():
    return {"Hello": "World"}

@app.get("/items/{item_id}/about")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/items/")
async def read_item(limit: int = 10 , skip: int = 0, sort: Optional[str] = None, db: Session = Depends(get_db)):
    return {"limit": limit, "skip": skip, "sort": sort}




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
'''
Now, you can run the application using the following command:
python app/main.py
'''
