# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from dsg_lib.logging_config import config_log
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.database_functions import DatabaseSession

config_log(logging_level="DEBUG")
DB = DatabaseSession("sqlite_memory")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Hello")
    DB.create_tables()
    yield
    print("Goodbye")


app = FastAPI(lifespan=lifespan, title="Async Testing")


@app.get("/")
async def root():
    return RedirectResponse("/docs", status_code=307)


@app.get("/db-info")
async def get_db_info():
    return {
        "type": DB.get_current_database_type(),
        "config": DB.get_database_config(),
        "tables": DB.get_tables(),
    }


@app.get("/users")
async def get_users() -> list:
    return []


@app.get("/users/{id}")
async def get_user_id(id: str) -> dict:
    return {}


@app.post("users/new")
async def post_user(name: str):
    return {}
