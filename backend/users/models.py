from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """Model for User"""
    __tablename__ = "User"
    
    name = Column(String, primary_key=True, unique=True, index=True)
    email = Column(String, unique=False, index=True)
    hashed_password = Column(String)