from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.educacion_ambiental
item_collection = database.get_collection("items")

def item_helper(item) -> dict:
    return {
        "id": item["id"],
        "question_number": item["question_number"],
        "description": item["description"]
    }
