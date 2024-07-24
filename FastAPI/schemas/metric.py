from pydantic import BaseModel

class MetricBase(BaseModel):
    id: int
    question_id: int
    responses: int = 0
    responses_edited: int = 0
    responses_deleted: int = 0

class MetricCreate(MetricBase):
    pass

class MetricUpdate(MetricBase):
    pass

class MetricInDB(MetricBase):
    id: int

class Metric(MetricInDB):
    pass
