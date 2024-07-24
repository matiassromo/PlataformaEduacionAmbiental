from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client.my_database

item_collection = database.get_collection("items")
user_collection = database.get_collection("users")

def item_helper(item) -> dict:
    return {
        "id": item["id"],
        "question_number": item["question_number"],
        "description": item["description"],
    }

def user_helper(user) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "hashed_password": user["hashed_password"],
    }
