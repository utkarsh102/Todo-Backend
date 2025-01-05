from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import jwt
import sqlite3
import logging
logging.basicConfig(level=logging.DEBUG)
from datetime import datetime, timedelta

# --- Configuration ---
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_database_connection():
    import os
    db_path = os.path.abspath("tasks.db")
    print(f"Using database at: {db_path}")
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


# --- Initialize Database ---
def initialize_database():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

initialize_database()

# --- Models ---
class Task(BaseModel):
    title: str
    description: str
    status: str = "pending"

class TaskResponse(Task):
    id: str

class TokenData(BaseModel):
    username: str

# --- Authentication ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token.decode('utf-8') if isinstance(token, bytes) else token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(username=payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return verify_token(credentials.credentials)

# --- FastAPI App ---
app = FastAPI()
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    logging.debug(f"Received login request: username={username}, password={password}")
    if username == "admin" and password == "password":
        access_token = create_access_token({"sub": username})
        logging.debug(f"Generated token: {access_token}")
        return {"access_token": access_token}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: Task, user: TokenData = Depends(get_current_user)):
    logging.debug(f"Creating task: {task.title}")
    task_id = str(uuid4())
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (id, title, description, status) VALUES (?, ?, ?, ?)",
                   (task_id, task.title, task.description, task.status))
    conn.commit()
    conn.close()
    logging.debug(f"Task created with ID: {task_id}")
    return {"id": task_id, **task.dict()}

@app.get("/tasks", response_model=List[TaskResponse])
def fetch_all_tasks(user: TokenData = Depends(get_current_user)):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.commit()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def fetch_task_by_id(task_id: str, user: TokenData = Depends(get_current_user)):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.commit()
    conn.close()
    if task:
        return dict(task)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task_status(task_id: str, status: str, user: TokenData = Depends(get_current_user)):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated_task = cursor.fetchone()
    conn.close()
    return dict(updated_task)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, user: TokenData = Depends(get_current_user)):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    conn.close()
    return {"message": "Task deleted successfully"}
