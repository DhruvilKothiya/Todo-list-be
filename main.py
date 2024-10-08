from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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