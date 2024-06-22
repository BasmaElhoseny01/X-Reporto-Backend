
from pydantic import BaseModel
from typing import Optional

class Error(BaseModel):
    detail: Optional[str] = None