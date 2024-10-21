from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from Models.user import TaskStatus, User
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base = declarative_base()

# Database Configuration
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

# FastAPI App Initialization
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class BaseTableSchema(BaseModel):
    title: str
    is_completed:bool =False


class UserSchema(BaseModel):
    email: str
    password: str



# Hash password using bcrypt
def get_password_hash(password):
    return pwd_context.hash(password)

# Verify password using bcrypt
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except :
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Token Endpoint for Login
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: UserSchema, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Create User Endpoint (Password will be hashed)
@app.post("/users/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    return crud.create_user(db, name=name, email=email, password=hashed_password)

# Read all users (Only accessible with a valid token)
@app.get("/users/")
def read_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_users(db)

# Update user (Only accessible with a valid token)
@app.put("/users/{user_id}")
def update_user( name: str, email: str, password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hashed_password = get_password_hash(password)
    user = crud.update_user(db, user_id=current_user.id, name=name, email=email, password=hashed_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Delete user (Only accessible with a valid token)
@app.delete("/users/{user_id}")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = crud.delete_user(db, user_id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Task Endpoints (Same as before but protected by token)
@app.post("/tasks/")
def create_task(item: BaseTableSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_task(db, user_id=current_user.id, title=item.title, is_completed=item.is_completed)

@app.get("/users/tasks/")
def get_tasks(search: str | int = None, sort: str = 'asc', limit: int = None, offset: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Logic remains the same
    query = db.query(TaskStatus).filter(TaskStatus.user_id == current_user.id)
    if search:
        query = query.filter(TaskStatus.title.ilike(f"%{search}%"))
    if sort == "asc":
        query = query.order_by(TaskStatus.title.asc())
    elif sort == "desc":
        query = query.order_by(TaskStatus.title.desc())
    total_count = query.count()
    tasks = query.offset(offset).limit(limit).all()
    return {"tasks": tasks, "total": total_count}

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = crud.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str, is_completed: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = crud.update_task(db, task_id=task_id, title=title, is_completed=is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = crud.delete_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
