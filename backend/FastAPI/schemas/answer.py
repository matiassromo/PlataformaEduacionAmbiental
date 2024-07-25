from pydantic import BaseModel

class Answer(BaseModel):
    _id: int
    answer: str

    class Config:
        schema_extra = {
            "example": {
                "_id": 1,
                "answer": "This is an example answer"
            }
        }
