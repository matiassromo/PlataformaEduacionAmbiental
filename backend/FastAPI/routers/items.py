from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from backend.database.database import item_collection, item_helper, metric_collection, metric_helper, generate_new_id
from backend.FastAPI.schemas.item import ItemCreate, ItemUpdate, Item, Answer
from bson import ObjectId
from typing import List
from backend.FastAPI.routers.users import get_current_user, User

router = APIRouter()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user)):
    existing_item = await item_collection.find_one({"id": item.id})
    if existing_item:
        raise HTTPException(status_code=400, detail="ID already exists")
    
    if item.id != item.question_number:
        raise HTTPException(status_code=400, detail="ID and question number must match")
    
    item = jsonable_encoder(item)
    new_item = await item_collection.insert_one(item)
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

    # Agrega la respuesta al item
    if 'answers' not in item:
        item['answers'] = []
    item['answers'].append(jsonable_encoder(answer))
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})

    # Actualizar métrica de respuestas
    existing_metric = await metric_collection.find_one({"question_id": item_id, "name": "responses"})
    if existing_metric:
        new_value = existing_metric["value"] + 1
        await metric_collection.update_one({"question_id": item_id, "name": "responses"}, {"$set": {"value": new_value}})
    else:
        new_metric_id = await generate_new_id("metrics_id")
        new_metric = {
            "id": new_metric_id,
            "question_id": item_id,
            "name": "responses",
            "value": 1
        }
        await metric_collection.insert_one(new_metric)
    
    return item_helper(item)

@router.put("/{item_id}/answer/{answer_id}", response_model=Item)
async def edit_answer(item_id: int, answer_id: int, new_answer: Answer, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for i, answer in enumerate(item['answers']):
        if answer['id'] == answer_id:
            item['answers'][i] = jsonable_encoder(new_answer)
            break
    else:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})
    return item_helper(item)

@router.delete("/{item_id}/answer/{answer_id}", response_model=Item)
async def delete_answer(item_id: int, answer_id: int, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item['answers'] = [answer for answer in item['answers'] if answer['id'] != answer_id]
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})
    return item_helper(item)

