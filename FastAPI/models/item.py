from typing import Optional
from pydantic import BaseModel, Field

class Question(BaseModel):
    name: str
    description: Optional[str] = None

class Challenge(BaseModel):
    title: str
    description: Optional[str] = None
