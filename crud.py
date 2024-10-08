from sqlalchemy.orm import Session
from Models.user import User
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

# Update user963.
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