# schemas/challenge.py
from pydantic import BaseModel

class ChallengeBase(BaseModel):
    title: str
    description: str

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(ChallengeBase):
    pass

class ChallengeInDB(ChallengeBase):
    id: str

class Challenge(ChallengeInDB):
    pass
