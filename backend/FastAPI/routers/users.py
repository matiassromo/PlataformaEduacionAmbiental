from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from backend.database.database import user_collection, user_helper
from bson import ObjectId
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDB(UserBase):
    id: str
    hashed_password: str

class User(UserInDB):
    pass

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.get("/", response_model=List[User])
async def get_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    user_dict = {"email": user.email, "hashed_password": hashed_password}
    new_user = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return user_helper(created_user)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate):
    user_dict = user.dict(exclude_unset=True)
    if "password" in user_dict:
        user_dict["hashed_password"] = pwd_context.hash(user_dict["password"])
        del user_dict["password"]
    update_result = await user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_dict})
    if update_result.modified_count == 1:
        updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if updated_user:
            return user_helper(updated_user)
    existing_user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if existing_user:
        return user_helper(existing_user)
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    delete_result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if delete_result.deleted_count == 1:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
