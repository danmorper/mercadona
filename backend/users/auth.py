from sqlalchemy.future import select
from . import models, security
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from .db import get_db
from jose import JWTError, jwt

# Asynchronous function for user authentication
async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).filter(models.User.name == username))
    user = result.scalars().first()
    if not user or not security.verify_password(password, user.hashed_password):
        return False
    return user

# Asynchronous function for user creation
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = security.hash_password(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Asynchronous function to get user by username
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.name == username))
    return result.scalars().first()