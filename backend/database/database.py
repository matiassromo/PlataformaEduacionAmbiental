from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client.educacion_ambiental

item_collection = database.get_collection("items")
user_collection = database.get_collection("users")
counter_collection = database.get_collection("counters")

async def get_next_sequence_value(sequence_name: str):
    result = await counter_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return result["sequence_value"]

def item_helper(item) -> dict:
    return {
        "id": item["id"],
        "question_number": item["question_number"],
        "description": item["description"],
        "answers": item.get("answers", []),
    }

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "hashed_password": user["hashed_password"],
    }

async def generate_new_id(sequence_name: str):
    result = await counter_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return result["sequence_value"]

async def update_existing_answers():
    async for item in item_collection.find():
        if "answers" not in item:
            item["answers"] = []
        for answer in item.get("answers", []):
            if "_id" not in answer:
                answer["_id"] = await generate_new_id("answer_id")
        await item_collection.update_one({"_id": item["_id"]}, {"$set": {"answers": item["answers"]}})
