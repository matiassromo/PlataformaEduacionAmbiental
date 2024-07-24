from pydantic import BaseModel

class ItemBase(BaseModel):
    id: int
    question_number: int
    description: str

class ItemCreate(ItemBase):
    id: int

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    id: int

class Item(ItemInDB):
    pass
