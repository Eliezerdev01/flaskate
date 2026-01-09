from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import hashlib
import os

app = FastAPI()

# Get these from your Supabase Project Settings > API
SUPABASE_URL = "https://hlfmolptnpcjzpviuqsf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserData(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(user: UserData):
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Insert into Supabase
    response = supabase.table("users").insert({
        "username": user.username, 
        "password": hashed_pw
    }).execute()
    
    return {"status": "success"}

@app.post("/login")
def login(user: UserData):
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Query Supabase
    response = supabase.table("users").select("*").eq("username", user.username).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="User not found")
    
    if response.data[0]["password"] == hashed_pw:
        return {"status": "success", "user": user.username}
    
    raise HTTPException(status_code=400, detail="Wrong password")
