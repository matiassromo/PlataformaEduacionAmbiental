from fastapi import APIRouter, HTTPException
from backend.database.database import metric_collection, metric_helper

router = APIRouter()

@router.get("/", response_model=list[dict])
async def get_metrics():
    metrics = []
    async for metric in metric_collection.find():
        metrics.append(metric_helper(metric))
    return metrics

@router.post("/reset/{metric_id}", response_model=dict)
async def reset_metric(metric_id: int):
    metric = await metric_collection.find_one({"id": metric_id})
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    updated_metric = {
        "responses": 0,
        "responses_edited": 0,
        "responses_deleted": 0,
    }
    await metric_collection.update_one({"id": metric_id}, {"$set": updated_metric})
    return {"message": "Metric reset successful"}
