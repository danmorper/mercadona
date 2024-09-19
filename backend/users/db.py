import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Retrieve database configuration from environment variables
user = os.getenv("DB_USER", "default_user")
password = os.getenv("DB_PASSWORD", "default_password")
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "default_db_name")

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"
print(DATABASE_URL)
# Create the engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session