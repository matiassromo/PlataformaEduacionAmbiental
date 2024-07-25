from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from backend.database.database import item_collection, item_helper, generate_new_id, counter_collection
from backend.FastAPI.routers.users import get_current_user, User
from backend.FastAPI.schemas.item import ItemCreate, ItemUpdate, Item
from typing import List

router = APIRouter()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user)):
    if item.id != item.question_number:
        raise HTTPException(status_code=400, detail="ID and question number must match")

    new_id = await generate_new_id("item_id")
    item.id = new_id
    item.question_number = new_id

    item_data = jsonable_encoder(item)
    new_item = await item_collection.insert_one(item_data)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

@router.get("/", response_model=List[Item])
async def get_items(current_user: User = Depends(get_current_user)):
    items = []
    async for item in item_collection.find().sort("id", 1):
        items.append(item_helper(item))
    return items

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate, current_user: User = Depends(get_current_user)):
    if item_id != item.question_number:
        raise HTTPException(status_code=400, detail="ID and question number must match")
    
    update_result = await item_collection.update_one({"id": item_id}, {"$set": item.dict()})
    if update_result.modified_count == 1:
        updated_item = await item_collection.find_one({"id": item_id})
        if updated_item is not None:
            return item_helper(updated_item)
    existing_item = await item_collection.find_one({"id": item_id})
    if existing_item is not None:
        return item_helper(existing_item)
    raise HTTPException(status_code=404, detail="Item not found")

async def reset_counter_if_empty():
    count = await item_collection.count_documents({})
    if count == 0:
        await counter_collection.update_one(
            {"_id": "item_id"},
            {"$set": {"sequence_value": 0}}
        )

@router.delete("/", response_model=dict)
async def delete_all_items(current_user: User = Depends(get_current_user)):
    await item_collection.delete_many({})
    await counter_collection.update_one(
        {"_id": "item_id"},
        {"$set": {"sequence_value": 0}}
    )
    return {"message": "All items deleted"}


