from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)

