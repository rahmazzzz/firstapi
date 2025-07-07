from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# MongoDB connection string — replace with your own!
MONGO_URI = "mongodb://localhost:27017/"  # Or your Atlas URI
client = AsyncIOMotorClient(MONGO_URI)
db = client["mydatabase"]
collection = db["users"]

# Pydantic Model
class User(BaseModel):
    name: str = Field(...)
    age: int = Field(...)

# Helper to convert ObjectId
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "age": user["age"]
    }

# Create
@app.post("/users")
async def create_user(user: User):
    user = user.dict()
    result = await collection.insert_one(user)
    new_user = await collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

# Read all
@app.get("/users")
async def get_users():
    users = []
    async for user in collection.find():
        users.append(user_helper(user))
    return users

# Read one
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    raise HTTPException(status_code=404, detail="User not found")

# Update
@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    user = user.dict()
    result = await collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user}
    )
    if result.modified_count == 1:
        updated_user = await collection.find_one({"_id": ObjectId(user_id)})
        return user_helper(updated_user)
    raise HTTPException(status_code=404, detail="User not found")

# Delete
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
