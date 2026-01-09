import os
import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
# 1. Load local .env file if it exists (for local development)
# Render will ignore this and use its own Environment Variables
load_dotenv()

app = FastAPI()

# 2. Connect to Supabase using Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY not found in Environment Variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Define the Data Model
class UserAuth(BaseModel):
    username: str
    password: str

# 4. Registration Endpoint
@app.post("/register")
async def register(user: UserAuth):
    # Hash the password before it ever touches the database
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    
    try:
        # Insert into the 'users' table you created in Supabase
        response = supabase.table("users").insert({
            "username": user.username,
            "password": hashed_pw
        }).execute()
        
        return {"status": "success", "message": "User registered successfully"}
    
    except Exception as e:
        # Supabase will throw an error if the username (Primary Key) already exists
        raise HTTPException(status_code=400, detail="Username already exists or database error")

# 5. Login Endpoint
@app.post("/login")
async def login(user: UserAuth):
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Query Supabase for this specific username
    response = supabase.table("users").select("*").eq("username", user.username).execute()
    
    # Check if user exists and password matches
    if response.data and response.data[0]["password"] == hashed_pw:
        return {
            "status": "success", 
            "message": "Login successful",
            "username": user.username
        }
    
    raise HTTPException(status_code=401, detail="Invalid username or password")

# 6. Health Check (To help Render keep the service 'warm')
@app.get("/")
async def root():
    return {"message": "API is online and connected to Supabase"}
