from fastapi import FastAPI, HTTPException
from FastAPI.routers import items, challenges  # Ruta completa desde la raíz del proyecto
from database.database import client  # Ruta correcta para el módulo de la base de datos

app = FastAPI()

@app.get("/check_db")
async def check_db_connection():
    try:
        await client.server_info()
        return {"status": "Connection to MongoDB is successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(items.router)
app.include_router(challenges.router)
