from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from backend.database.database import item_collection, generate_new_id
from backend.FastAPI.schemas.answer import Answer
from backend.FastAPI.routers.users import get_current_user, User
from typing import List

router = APIRouter()

@router.get("/{item_id}/answers", response_model=List[Answer])
async def get_answers(item_id: int, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    answers = item.get("answers", [])
    for answer in answers:
        if "_id" not in answer:
            answer["_id"] = await generate_new_id("answer_id")
            await item_collection.update_one({"id": item_id}, {"$set": {"answers": answers}})
    
    return answers

@router.post("/{item_id}/answer", response_model=dict)
async def answer_question(item_id: int, answer: Answer, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    answer_id = await generate_new_id("answer_id")
    answer_data = jsonable_encoder(answer)
    answer_data["_id"] = answer_id

    if 'answers' not in item:
        item['answers'] = []
    item['answers'].append(answer_data)
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item["answers"]}})

    return {"message": "Answer added successfully", "answer": answer_data}

@router.put("/{item_id}/answer/{answer_id}", response_model=dict)
async def edit_answer(item_id: int, answer_id: int, new_answer: Answer, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for i, answer in enumerate(item['answers']):
        if answer['_id'] == answer_id:
            item['answers'][i] = jsonable_encoder(new_answer)
            item['answers'][i]["_id"] = answer_id
            break
    else:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})
    return {"message": "Answer updated successfully"}

@router.delete("/{item_id}/answer/{answer_id}", response_model=dict)
async def delete_answer(item_id: int, answer_id: int, current_user: User = Depends(get_current_user)):
    item = await item_collection.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item['answers'] = [answer for answer in item['answers'] if answer['_id'] != answer_id]
    await item_collection.update_one({"id": item_id}, {"$set": {"answers": item['answers']}})
    return {"message": "Answer deleted successfully"}
