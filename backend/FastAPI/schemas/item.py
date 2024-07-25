from pydantic import BaseModel
from typing import List

class Answer(BaseModel):
    _id: int
    answer: str

class ItemBase(BaseModel):
    id: int
    question_number: int
    description: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    answers: List[Answer] = []

class Item(ItemInDB):
    pass
