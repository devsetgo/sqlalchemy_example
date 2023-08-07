# -*- coding: utf-8 -*-
from enum import Enum
import secrets
from functools import lru_cache
from datetime import datetime  # A Python library used for working with dates and times
from pydantic import (
    BaseSettings,  # A library for data validation and settings management
    PostgresDsn,
)
from pydantic import validator


class DatabaseDriverEnum(
    str, Enum
):  # creating an Enum class to hold database driver values
    postgres = "postgresql+asyncpg"  # defining the value for postgres driver
    sqlite = "sqlite+aiosqlite"  # defining the value for sqlite driver
    memory = "sqlite+aiosqlite:///:memory:?cache=shared"
    mysql = "mysql+aiomysql"  # defining the value for mysql driver
    oracle = "oracle+cx_oracle"  # defining the value for oracle driver

    class Config:  # creating a nested class to hold configuration options for the Enum class
        use_enum_values = True  # setting the configuration option to use the Enum values instead of their names



class Settings(BaseSettings):
    # Use the DatabaseDriverEnum Enum for DB_TYPE
    database_driver: DatabaseDriverEnum
    db_user: str = None
    db_password: str = None
    db_host: str = None
    db_port: int = 5432
    db_name: str = None
    secret_key: str = secrets.token_hex(128)
    # Set the current date and time when the application is run
    date_run: datetime = datetime.utcnow()

    def database_uri(self) -> str:
        if self.database_driver == DatabaseDriverEnum.memory:
            return str(self.database_driver)
        return f"{self.database_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def dict(self):
        original_dict = super().dict()
        original_dict.update({"database_uri": self.database_uri()})
        return original_dict
    
    @validator("database_driver", pre=True)
    def parse_database_driver(cls, value):
        """
        Validator function to convert the input string to the corresponding enum member value.

        Args:
            value (str): The input string to be converted.

        Returns:
            The corresponding enum member value if the input string is valid, otherwise returns the input value.
        """
        if isinstance(value, str):
            try:
                return DatabaseDriverEnum[value]
            except KeyError:
                pass
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        use_enum_values = True

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
