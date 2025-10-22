from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

app = FastAPI(title="User Management API")

users_db = {}

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)



@app.post("/users/")
def create_user(user: User):
    user_id = len(users_db) + 1
    for existing in users_db.values():
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    users_db[user_id] = user.dict()
    return {"id": user_id, "message": "User added successfully"}


@app.get("/users/")
def read_users(limit: Optional[int] = Query(None, ge=1)):
    all_users = [{"id": uid, **data} for uid, data in users_db.items()]
    if limit:
        all_users = all_users[:limit]
    return all_users


@app.put("/users/{user_id}")
def update_user(user_id: int = Path(..., ge=1), user: UserUpdate = None):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    stored_user = users_db[user_id]
    update_data = user.dict(exclude_unset=True)
    stored_user.update(update_data)
    users_db[user_id] = stored_user
    return {"message": "User updated successfully"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int = Path(..., ge=1)):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return {"message": "User deleted successfully"}
