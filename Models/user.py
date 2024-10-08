from sqlalchemy import Column, Integer, String,Boolean
from database import Base   
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # is_completed=Column(Boolean,default=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)