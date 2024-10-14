from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
import os


Base = declarative_base()
DATABASE_USER_NAME = 'root'
DATABASE_PASSWORD = 'password'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
DATABASE_NAME = 'test_1'
DATABASE_URL = f"mysql+mysqldb://{DATABASE_USER_NAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
# Create a session factory bound to our engine
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Dependency function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create User
@app.post("/users/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    return crud.create_user(db, name=name, email=email, password=password)

# Read all users
@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

# Update user
@app.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str, password: str, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id=user_id, name=name, email=email, password=password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.delete_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# Task endpoints (new code)

# Create a new task for a user
@app.post("/tasks/")
def create_task(user_id: int, title:str,is_completed: bool = False, db: Session = Depends(get_db)):
    return crud.create_task(db, user_id=user_id,title=title, is_completed=is_completed)

# Get all tasks for a specific user
@app.get("/users/{user_id}/tasks/")
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, user_id=user_id)
    return tasks


# Update task
@app.put("/tasks/{task_id}")
def update_task(task_id: int,title:str, is_completed: bool, db: Session = Depends(get_db)):

    task = crud.update_task(db, task_id=task_id,title=title, is_completed=is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Get task by task_id
@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}