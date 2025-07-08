from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# MongoDB connection string — replace with your own! # Or your Atlas URI
client = MongoClient("DATABASE_UR")
db = client.user_db
collection = db.users

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
@app.post("/create_user")
def create_user(user: User):
    user = user.dict()
    result =  collection.insert_one(user)
    new_user =  collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

# Read all
@app.get("/get_users")
def get_users():
    users = []
    for user in collection.find():
        users.append(user_helper(user))
    return users

# Read one
@app.get("/get_user/{user_id}")
def get_user(user_id: str):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    raise HTTPException(status_code=404, detail="User not found")

# Update
@app.put("/update_user/{user_id}")
def update_user(user_id: str, user: User):
    user = user.dict()
    result = collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user}
    )
    if result.modified_count == 1:
        updated_user = collection.find_one({"_id": ObjectId(user_id)})
        return user_helper(updated_user)
    raise HTTPException(status_code=404, detail="User not found")

# Delete
@app.delete("/delete_user/{user_id}")
def delete_user(user_id: str):
    result = collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
