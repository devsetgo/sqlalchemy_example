# -*- coding: utf-8 -*-
import secrets
import logging
from datetime import datetime
from uuid import uuid4, UUID
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, MetaData, DateTime, text, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from dsg_lib.logging_config import config_log
from src.settings import settings


config_log(
    logging_directory="logs",
    log_name="log.log",
    logging_level="WARNING",
    log_rotation="100 MB",
    log_retention="5 days",
    log_backtrace=True,
    log_format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer=False,
    # log_diagnose=True,
    # app_name="myapp",
    # append_app_name=True,
    # service_id="12345",
    # append_service_id=True,
)


class AsyncDatabase:
    metadata = MetaData()

    # Initialize engine
    # DATABASE_URL= "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"
    # SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///app.db"
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Define base model to produce tables
    Base = declarative_base(metadata=metadata)

    # Create async sessionmaker
    sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @classmethod
    async def create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(cls.Base.metadata.create_all)

    @asynccontextmanager
    async def get_db_session(self):
        db_session = self.sessionmaker()
        try:
            yield db_session
        finally:
            await db_session.commit()
            await db_session.close()


class DBHandler:
    @classmethod
    async def count_query(cls, query):
        async with AsyncDatabase().get_db_session() as session:
            # Modifying this line
            result = await session.execute(select(func.count()).select_from(query))

            return result.scalar()

    @classmethod
    async def fetch_query(cls, query, limit=500, offset=0):
        async with AsyncDatabase().get_db_session() as session:
            result = await session.execute(query.limit(limit).offset(offset))
            return result.scalars().all()

    @classmethod
    async def fetch_queries(cls, queries: dict, limit=500, offset=0):
        results = {}
        async with AsyncDatabase().get_db_session() as session:
            for query_name, query in queries.items():
                result = await session.execute(query.limit(limit).offset(offset))
                results[query_name] = result.scalars().all()
        return results

    @classmethod
    async def execute_one(cls, record):
        try:
            async with AsyncDatabase().get_db_session() as session:
                session.add(record)
                await session.commit()
            logging.info("Record operation successful")
            return record
        except Exception as ex:
            logging.error(f"Failed to perform operation on record: {ex}")
            raise HTTPException(status_code=400, detail="Operation failed on record")

    @classmethod
    async def execute_many(cls, records: List):
        try:
            async with AsyncDatabase().get_db_session() as session:
                session.add_all(records)
                await session.commit()
            logging.info("All record operations were successful")
            return records
        except Exception as ex:
            logging.error(f"Failed to perform operations on records: {ex}")
            raise HTTPException(status_code=400, detail="Operations failed on records")


class SchemaBase:
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    date_created = Column(DateTime, index=True, default=datetime.utcnow)
    date_updated = Column(
        DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(SchemaBase, AsyncDatabase.Base):
    __tablename__ = "users"

    name = Column(String, unique=False, index=True)
    # email = Column(String, unique=False, index=True)


class UserBase(BaseModel):
    name: str = Field(..., description="the users name")
    # email: str = Field(None, description="The users email address")

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: str
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: List[UserBase]


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await AsyncDatabase.create_tables()


@app.get("/")
async def root():
    return RedirectResponse("/docs", status_code=307)


@app.get("/users/count/")
async def count_users():
    count = await DBHandler.count_query(select(User))
    return {"count": count}


@app.get("/users/")
async def read_users():
    query=select(User)
    total_count = await DBHandler.count_query(query=query)
    users = await DBHandler.fetch_query(query=query)
    return {
        "query_data": {"total_count": total_count, "count": len(users)},
        "users": users,
    }


@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserBase):
    db_user = User(name=user.name)
    created_user = await DBHandler.execute_one(db_user)
    return created_user


@app.post("/users/bulk/", response_model=List[UserResponse])
async def create_users(user_list: UserList):
    db_users = [User(name=user.name) for user in user_list.users]
    created_users = await DBHandler.execute_many(db_users)
    return created_users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    users = await DBHandler.fetch_query(select(User).where(User.id == user_id))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]

@app.get("/database_type/")
async def database_type():
    async with AsyncDatabase().get_db_session() as session:
        try:
            result = await session.execute(text('SELECT version();'))  # change this query based on your DBMS
            return {"database_type": result}  # change this response based on your DBMS
        except Exception as e:
            return {"error": str(e)}

@app.get("/config")
async def get_config():
    return settings.dict()