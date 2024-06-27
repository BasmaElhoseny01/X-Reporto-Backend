from pydantic import BaseModel

class Document(BaseModel):
    id: int
    title: str
    content: str
