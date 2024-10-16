from sqlalchemy import Column, Integer, String,Boolean,ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class TaskStatus(Base):
    __tablename__='task_status'

    id=Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    title = Column(String,unique=True,index=True)
    is_completed = Column(Boolean, default=False)