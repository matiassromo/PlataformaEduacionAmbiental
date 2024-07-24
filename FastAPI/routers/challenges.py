from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.database import challenge_collection, challenge_helper
from FastAPI.schemas.challenge import ChallengeCreate, ChallengeUpdate, Challenge  # Ajusta la ruta
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Challenge)
async def create_challenge(challenge: ChallengeCreate):
    challenge = jsonable_encoder(challenge)
    new_challenge = await challenge_collection.insert_one(challenge)
    created_challenge = await challenge_collection.find_one({"_id": new_challenge.inserted_id})
    return challenge_helper(created_challenge)

@router.get("/", response_model=list[Challenge])
async def get_challenges():
    challenges = []
    async for challenge in challenge_collection.find():
        challenges.append(challenge_helper(challenge))
    return challenges

@router.get("/{challenge_id}", response_model=Challenge)
async def get_challenge(challenge_id: str):
    challenge = await challenge_collection.find_one({"_id": ObjectId(challenge_id)})
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge_helper(challenge)

@router.put("/{challenge_id}", response_model=Challenge)
async def update_challenge(challenge_id: str, challenge: ChallengeUpdate):
    challenge = {k: v for k, v in challenge.dict().items() if v is not None}
    update_result = await challenge_collection.update_one({"_id": ObjectId(challenge_id)}, {"$set": challenge})
    if update_result.modified_count == 1:
        if (updated_challenge := await challenge_collection.find_one({"_id": ObjectId(challenge_id)})) is not None:
            return challenge_helper(updated_challenge)
    if (existing_challenge := await challenge_collection.find_one({"_id": ObjectId(challenge_id)})) is not None:
        return challenge_helper(existing_challenge)
    raise HTTPException(status_code=404, detail="Challenge not found")

@router.delete("/{challenge_id}", response_description="Delete a challenge")
async def delete_challenge(challenge_id: str):
    delete_result = await challenge_collection.delete_one({"_id": ObjectId(challenge_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Challenge deleted"}
    raise HTTPException(status_code=404, detail="Challenge not found")
