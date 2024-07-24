from fastapi import FastAPI, HTTPException
from FastAPI.routers.items import router as items_router
from database.database import client  

app = FastAPI()

@app.get("/check_db")
async def check_db_connection():
    try:
        await client.server_info()
        return {"status": "Connection to MongoDB is successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(items_router, prefix="/items", tags=["items"])
