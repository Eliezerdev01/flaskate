from fastapi import FastAPI
from pydantic import BaseModel
import hashlib

app = FastAPI()

# For this example, we use a dictionary. In production, 
# this is where you'd connect to PostgreSQL or Supabase.
fake_db = {"admin": hashlib.sha256("admin123".encode()).hexdigest()}

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    hashed_p = hashlib.sha256(user.password.encode()).hexdigest()
    if user.username in fake_db and fake_db[user.username] == hashed_p:
        return {"status": "success", "message": "Login successful"}
    return {"status": "error", "message": "Invalid credentials"}
