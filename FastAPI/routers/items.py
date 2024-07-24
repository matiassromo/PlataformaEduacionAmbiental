from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from database.database import item_collection, item_helper, metric_collection, metric_helper
from FastAPI.schemas.item import ItemCreate, ItemUpdate, Item, Answer
from bson import ObjectId
from typing import List
from FastAPI.routers.users import get_current_user, User

router = APIRouter()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user)):
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

@router.get("/", response_model=List[Item])
async def get_items(current_user: User = Depends(get_current_user)):
    items = []
    async for item in item_collection.find().sort("id", 1):  # Ordenar por id en orden ascendente
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
async def delete_item(item_id: int, current_user: User = Depends(get_current_user)):
    delete_result = await item_collection.delete_one({"id": item_id})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/{item_id}/answer", response_model=Item)
async def answer_question(item_id: int, answer: Answer, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item['answers'].append(jsonable_encoder(answer))
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})

    # Actualizar métrica de respuestas
    existing_metric = await metric_collection.find_one({"question_id": item_id, "name": "responses"})
    if existing_metric:
        new_value = existing_metric["value"] + 1
        await metric_collection.update_one({"question_id": item_id, "name": "responses"}, {"$set": {"value": new_value}})
    else:
        new_metric = {
            "id": generate_new_id(),  # Asegúrate de tener una función para generar nuevos IDs
            "question_id": item_id,
            "name": "responses",
            "value": 1
        }
        await metric_collection.insert_one(new_metric)
    
    return item_helper(item)
