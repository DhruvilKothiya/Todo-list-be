from sqlalchemy.orm import Session
from Models.user import User
from Models.user import TaskStatus

# User CRUD operations

# Create a new user
def create_user(db: Session, name: str, email: str, password: str):
    user = User(name=name, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Read users
def get_users(db: Session):
    return db.query(User).all()

# Update user
def update_user(db: Session, user_id: int, name: str, email: str, password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.email = email
        user.password = password
        db.commit()
        db.refresh(user)
    return user

# Delete user
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

# Task CRUD operations

# Create a new task for a user
def create_task(db: Session, user_id: int, title: str, is_completed: bool = False):
    task = TaskStatus(user_id=user_id, title=title, is_completed=is_completed)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

## Read all tasks for a user with optional search and sort functionality
def get_tasks(db: Session, user_id: int, search: str | int = None   , sort: str = "asc"):
    query = db.query(TaskStatus).filter(TaskStatus.user_id == user_id)
    
    if search:
        query = query.filter(TaskStatus.title.ilike(f"%{search}%"))  # Case-insensitive search
    
    if sort == "asc":
        query = query.order_by(TaskStatus.title.asc())
    elif sort == "desc":
        query = query.order_by(TaskStatus.title.desc())
    
    return query.all()

# Read task by task_id
def get_task_by_id(db: Session, task_id: int):
    return db.query(TaskStatus).filter(TaskStatus.id == task_id).first()

# Update task
def update_task(db: Session, task_id: int, title: str, is_completed: bool):
    task = db.query(TaskStatus).filter(TaskStatus.id == task_id).first()
    if task:
        task.title = title
        task.is_completed = is_completed
        db.commit()
        db.refresh(task)
    return task

# Delete task
def delete_task(db: Session, task_id: int):
    task = db.query(TaskStatus).filter(TaskStatus.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task
