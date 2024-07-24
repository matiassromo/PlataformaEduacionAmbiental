from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"  # Actualiza esto con tu URI de MongoDB

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client.my_database_name  # Reemplaza con el nombre de tu base de datos

item_collection = database.get_collection("items")
challenge_collection = database.get_collection("challenges")

# Helpers (opcional)
def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item["description"]
    }

def challenge_helper(challenge) -> dict:
    return {
        "id": str(challenge["_id"]),
        "title": challenge["title"],
        "description": challenge["description"]
    }
