from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database.database import user_collection, user_helper
import logging
from bson import ObjectId
from typing import Optional

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    id: int
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDB(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str

@router.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate):
    logging.info(f"Attempting to register user with email: {user.email}")
    existing_user = await user_collection.find_one({"id": user.id})
    if existing_user:
        logging.warning(f"ID already registered: {user.id}")
        raise HTTPException(status_code=400, detail="ID already registered")
    
    existing_email = await user_collection.find_one({"email": user.email})
    if existing_email:
        logging.warning(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    user_dict = {"id": user.id, "email": user.email, "hashed_password": hashed_password}
    logging.info(f"Inserting user into database: {user_dict}")
    new_user = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    logging.info(f"User created with ID: {created_user['_id']}")
    return user_helper(created_user)

@router.get("/", response_model=list[UserInDB])
async def get_users():
    users = []
    async for user in user_collection.find().sort("id", 1):
        users.append(user_helper(user))
    return users

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: int):
    user = await user_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(user_id: int, user: UserUpdate):
    user_data = {k: v for k, v in user.dict().items() if v is not None}
    if "password" in user_data:
        user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))
    update_result = await user_collection.update_one({"id": user_id}, {"$set": user_data})
    if update_result.modified_count == 1:
        updated_user = await user_collection.find_one({"id": user_id})
        if updated_user:
            return user_helper(updated_user)
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", response_description="Delete a user")
async def delete_user(user_id: int):
    delete_result = await user_collection.delete_one({"id": user_id})
    if delete_result.deleted_count == 1:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
