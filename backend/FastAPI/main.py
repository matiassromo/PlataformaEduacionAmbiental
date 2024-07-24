from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.FastAPI.routers import items, users, metrics
import logging

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de logging
logging.basicConfig(level=logging.INFO)

@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    logging.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
