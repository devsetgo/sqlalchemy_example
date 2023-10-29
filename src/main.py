# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from dsg_lib.logging_config import config_log
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Column, String
from sqlalchemy.future import select

from . import tools
from .base_schema import SchemaBase
from .database_connector import AsyncDatabase
from .database_ops import DatabaseOperations

config_log(
    logging_directory="logs",
    log_name="log.log",
    logging_level="DEBUG",
    log_rotation="100 MB",
    log_retention="1 days",
    log_backtrace=True,
    log_format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer=False,
    # log_diagnose=True,
    # app_name="myapp",
    # append_app_name=True,
    # service_id="12345",
    # append_service_id=True,
)


class User(SchemaBase, AsyncDatabase.Base):
    __tablename__ = "users"

    name_first = Column(String, unique=False, index=True)
    name_last = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True)


class UserBase(BaseModel):
    name_first: str = Field(
        ...,
        # alias="firstName",
        description="the users first or given name",
        examples=["Bob"],
    )
    name_last: str = Field(
        ...,
        # alias="lastName",
        description="the users last or surname name",
        examples=["Fruit"],
    )
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    _id: str
    date_created: datetime
    date_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserBase]


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await AsyncDatabase.create_tables()


# Endpoint routers
router_responses: dict = {
    302: {"description": "The item was moved"},
    400: {"description": "Bad request"},
    401: {"description": "Unauthorized"},
    403: {"description": "Insufficient privileges"},
    404: {"description": "Not found"},
    418: {
        "I_am-a_teapot": "The server refuses the attempt to \
                brew coffee with a teapot."
    },
    429: {"description": "Rate limit exceeded"},
}


@app.get("/")
async def root():
    return RedirectResponse("/docs", status_code=307)


@app.get("/users/count/")
async def count_users():
    count = await DatabaseOperations.count_query(select(User))
    return {"count": count}


@app.get("/users/")
async def read_users(
    limit: int = Query(None, alias="limit", ge=1, le=1000), offset: int = 0
):
    if limit is None:
        limit = 500

    query_count = select(User)
    total_count = await DatabaseOperations.count_query(query=query_count)
    query = select(User)
    users = await DatabaseOperations.fetch_query(
        query=query, limit=limit, offset=offset
    )
    return {
        "query_data": {"total_count": total_count, "count": len(users)},
        "users": users,
    }


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase):
    db_user = User(
        name_first=user.name_first, name_last=user.name_last, email=user.email
    )
    created_user = await DatabaseOperations.execute_one(db_user)
    return created_user


@app.post(
    "/users/bulk/",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users(user_list: UserList):
    db_users = [
        User(name_first=user.name_first, name_last=user.name_last, email=user.email)
        for user in user_list.users
    ]
    created_users = await DatabaseOperations.execute_many(db_users)
    return created_users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    users = await DatabaseOperations.fetch_query(select(User).where(User.id == user_id))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]


# Tools router
app.include_router(
    tools.router,
    prefix="/api/v1/tools",
    tags=["tools"],
    responses=router_responses,
)
