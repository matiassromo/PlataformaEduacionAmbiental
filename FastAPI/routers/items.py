from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database.database import item_collection, item_helper
from FastAPI.schemas.item import ItemCreate, ItemUpdate, Item
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    # Verificar que el id no se repita
    existing_item = await item_collection.find_one({"id": item.id})
    if existing_item:
        raise HTTPException(status_code=400, detail="ID already exists")
    
    # Verificar que id y question_number coincidan
    if item.id != item.question_number:
        raise HTTPException(status_code=400, detail="ID and question number must match")
    
    item = jsonable_encoder(item)
    new_item = await item_collection.insert_one(item)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

"""@router.get("/", response_model=list[Item])
async def get_items():
    items = []
    async for item in item_collection.find():
        items.append(item_helper(item))
    return items"""

@router.get("/", response_model=list[Item])
async def get_items():
    items = []
    async for item in item_collection.find().sort("id", 1):  # Ordenar por id en orden ascendente
        items.append(item_helper(item))
    return items


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    item = await item_collection.find_one({"id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    # Asegurar que el id y el question_number coincidan en la actualización
    if item.question_number and item_id != item.question_number:
        raise HTTPException(status_code=400, detail="ID and question number must match")
    
    item = {k: v for k, v in item.dict().items() if v is not None}
    update_result = await item_collection.update_one({"id": item_id}, {"$set": item})
    if update_result.modified_count == 1:
        updated_item = await item_collection.find_one({"id": item_id})
        if updated_item is not None:
            return item_helper(updated_item)
    existing_item = await item_collection.find_one({"id": item_id})
    if existing_item is not None:
        return item_helper(existing_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}", response_description="Delete an item")
async def delete_item(item_id: int):
    delete_result = await item_collection.delete_one({"id": item_id})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")