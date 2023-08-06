# Import necessary modules
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData

# Define metadata object
metadata = MetaData()

# Create async engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Update this with your DB URL
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)


# Define base model to produce tables
class Base:
    metadata = metadata


# Assuming you have a User model defined as follows:
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


# Now let's use the `run_sync` method to perform synchronous operations
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Run the function to create tables
import asyncio

asyncio.run(create_tables())
