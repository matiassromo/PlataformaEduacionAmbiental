from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.database import item_collection, item_helper
from FastAPI.schemas.item import ItemCreate, ItemUpdate, Item  # Ajusta la ruta
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    item = jsonable_encoder(item)
    new_item = await item_collection.insert_one(item)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

@router.get("/", response_model=list[Item])
async def get_items():
    items = []
    async for item in item_collection.find():
        items.append(item_helper(item))
    return items

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: str):
    item = await item_collection.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemUpdate):
    item = {k: v for k, v in item.dict().items() if v is not None}
    update_result = await item_collection.update_one({"_id": ObjectId(item_id)}, {"$set": item})
    if update_result.modified_count == 1:
        if (updated_item := await item_collection.find_one({"_id": ObjectId(item_id)})) is not None:
            return item_helper(updated_item)
    if (existing_item := await item_collection.find_one({"_id": ObjectId(item_id)})) is not None:
        return item_helper(existing_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}", response_description="Delete item")
async def delete_item(item_id: str):
    delete_result = await item_collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
