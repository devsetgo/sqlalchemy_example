# -*- coding: utf-8 -*-

"""
This script contains the AsyncDatabaseSession class which is used for managing database engines 
for different types of databases using SQLAlchemy's async engine.

Usage examples:

1. Instantiate the AsyncDatabaseSession:

    ```python
    db_session = AsyncDatabaseSession("sqlite_memory")
    ```

2. Get supported databases:

    ```python
    supported_databases = db_session.get_supported_databases()
    print(supported_databases)
    ```

3. Set a new database type:

    ```python
    db_session.set_database_type("postgresql")
    ```

4. Get current database type:

    ```python
    current_db_type = db_session.get_current_database_type()
    print(current_db_type)
    ```

5. Update database configuration:

    ```python
    new_config = {"echo": False}
    db_session.update_database_config(new_config)
    ```

6. Create a session and perform operations:

    ```python
    async with db_session as session:
        # Perform database operations
    ```

7. Create tables:

    ```python
    await db_session.create_tables()
    ```

8. Get all table names:

    ```python
    table_names = await db_session.get_tables()
    print(table_names)
    ```

Please note that these are simple usage examples, actual usage may vary based on your application needs.
"""

import logging

from sqlalchemy import MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

metadata = MetaData()
Base = declarative_base(metadata=metadata)

import logging

from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.orm import sessionmaker

SYNC_DATABASE_CONFIG = {
    # "mysql": {
    #     "url": "mysql+aiomysql://username:password@host/database",
    #     "echo": False,
    #     "pool_size": 15,
    #     "charset": "utf8mb4",
    # },
    # "oracle": {
    #     "url": "oracle+cx_oracle://username:password@host:port/service_name",
    #     "echo": True,
    #     "pool_size": 8,
    #     "timeout": 10,
    # },
    # "postgresql": {
    #     "url": "postgresql+asyncpg://username:password@localhost/database",
    #     "echo": True,
    #     "pool_size": 10,
    #     "max_overflow": 20,
    #     "ssl": False,
    # },
    "sqlite": {
        "url": "sqlite:///database.db",
        "echo": True,
        # "pool_size": 10,
    },
    "sqlite_memory": {"url": "sqlite:///:memory:", "echo": True, "future": True},
}

import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


class DatabaseSession:
    """
    A class for managing database engines for different types of databases using SQLAlchemy's engine.
    """

    def __init__(self, db_type):
        """
        Constructor for the DatabaseEngine class.
        """
        logging.debug(f"Initializing DatabaseEngine with db_type: {db_type}")
        self.db_type = db_type
        self.sync_database_config = SYNC_DATABASE_CONFIG
        self.base = Base
        self.database_config = self._get_database_config()

        self._engine = None
        self._session = None

    def _get_database_config(self):
        """
        Private method that retrieves the database configuration based on the specified database type.

        Returns:
        - A dictionary containing the database configurations.
        """
        # config = self.sync_database_config.get(self.db_type)
        config = SYNC_DATABASE_CONFIG.get(self.db_type)
        if config is None:
            raise ValueError("Invalid database type")
        return config

    def get_supported_databases(self):
        """
        Returns a list of supported database types.
        """
        return list(self.sync_database_config.keys())

    def set_database_type(self, db_type):
        """
        Sets the database type to connect to.

        Parameters:
        - db_type: The type of the database to connect to (e.g., "postgresql", "sqlite", "oracle", or "mysql").
        """
        if not isinstance(db_type, str):
            raise TypeError("The db_type must be a string.")
        self.db_type = db_type
        self.database_config = self._get_database_config()

    def get_current_database_type(self):
        """
        Returns the currently set database type.
        """
        return self.db_type

    def get_database_config(self):
        """
        Returns the current database configuration.
        """
        return self.database_config

    def update_database_config(self, new_config):
        """
        Updates the database configuration with the provided new configuration.

        Parameters:
        - new_config: A dictionary containing the new database configurations to be updated.
        """
        if not isinstance(new_config, dict):
            raise TypeError("new_config must be a dictionary.")
        self.database_config.update(new_config)

    def create_engine(self):
        """
        Creates and returns a SQLAlchemy engine for the specified database.
        """
        url = self.database_config.pop("url", None)
        engine = create_engine(url, **self.database_config)
        return engine

    def get_session(self):
        """
        Returns a session object using the SQLAlchemy engine.
        """
        if not self._session:
            if not self._engine:
                self._engine = self.create_engine()
            Session = sessionmaker(bind=self._engine)
            self._session = Session()
        return self._session

    def close(self):
        """
        Closes the current session.
        """
        if self._session:
            self._session.close()
            self._session = None

    def create_tables(self):
        """
        Creates tables in the database.
        """
        if self._engine is None:
            self._engine = self.create_engine()
        self.base.metadata.create_all(self._engine)

        # Log table names
        inspector = inspect(self._engine)
        table_names = inspector.get_table_names()
        logging.info(table_names)

    def get_tables(self):
        """
        Retrieves and returns a list of all table names in the database.
        """
        inspector = inspect(self._engine)
        return inspector.get_table_names()


ASYNC_DATABASE_CONFIG = {
    # "mysql": {
    #     "url": "mysql+aiomysql://username:password@host/database",
    #     "echo": False,
    #     "pool_size": 15,
    #     "charset": "utf8mb4",
    # },
    # "oracle": {
    #     "url": "oracle+cx_oracle://username:password@host:port/service_name",
    #     "echo": True,
    #     "pool_size": 8,
    #     "timeout": 10,
    # },
    # "postgresql": {
    #     "url": "postgresql+asyncpg://username:password@localhost/database",
    #     "echo": True,
    #     "pool_size": 10,
    #     "max_overflow": 20,
    #     "ssl": False,
    # },
    "sqlite": {
        "url": "sqlite+aiosqlite:///database.db",
        "echo": True,
        # "pool_size": 10,
    },
    "sqlite_memory": {
        "url": "sqlite+aiosqlite:///:memory:?cache=shared",
        "echo": True,
    },
}


class AsyncDatabaseSession:
    """
    A class for managing database engines for different types of databases using SQLAlchemy's async engine.
    """

    def __init__(self, db_type):
        """
        Constructor for the DatabaseEngine class.

        Parameters:
        - db_type: The type of the database to connect to (e.g., "postgresql", "sqlite", "oracle", or "mysql").
        """
        logging.debug(
            f"Initializing DatabaseEngine with db_type: {db_type}"
        )  # Debug log
        self.db_type = db_type
        self.database_config = self._get_database_config()

        try:
            self._engine = self.create_engine()
        except SQLAlchemyError as ex:
            logging.error(f"An error occurred while creating the engine: {str(ex)}")
            self._engine = None
            raise

        self._session = None

    def _get_database_config(self):
        """
        Private method that retrieves the database configuration based on the specified database type.

        Returns:
        - A dictionary containing the database configurations.
        """
        try:
            logging.debug(
                f"Retrieving database config for db_type: {self.db_type}"
            )  # Debug log
            config = ASYNC_DATABASE_CONFIG.get(self.db_type)
            if config is None:
                raise ValueError("Invalid database type")
            return config
        except ValueError as ex:
            logging.error(f"An error occurred: {str(ex)}")
            raise  # re-raise the exception

    def create_engine(self):
        """
        Creates and returns a SQLAlchemy async engine for the specified database.

        Returns:
        - A SQLAlchemy async engine object.
        """
        try:
            logging.debug(f"Creating engine for db_type: {self.db_type}")  # Debug log
            url = self.database_config.pop(
                "url"
            )  # Remove 'url' from the dictionary and store its value
            engine = create_async_engine(url, **self.database_config)
            self.database_config["url"] = url  # Add 'url' back to the dictionary
            return engine
        except KeyError as ex:
            logging.error(
                f"An error occurred while creating engine: Missing key {str(ex)} in database configuration"
            )
            raise  # re-raise the exception

    def get_supported_databases(self):
        """
        Returns a list of supported database types.
        """
        try:
            logging.debug("Getting the list of supported databases.")  # Debug log
            return list(ASYNC_DATABASE_CONFIG.keys())
        except NameError as ex:
            logging.error(
                f"An error occurred while getting supported databases: {str(ex)}"
            )
            raise  # re-raise the exception

    def set_database_type(self, db_type):
        """
        Sets the database type to connect to.

        Parameters:
        - db_type: The type of the database to connect to (e.g., "postgresql", "sqlite", "oracle", or "mysql").
        """
        try:
            if not isinstance(db_type, str):
                error = "The db_type must be a string."
                logging.error(error)
                raise TypeError(error)

            logging.debug(f"Setting the database type to {db_type}.")  # Debug log
            self.db_type = db_type
            self.database_config = self._get_database_config()

        except TypeError as ex:
            logging.error(f"An error occurred while setting database type: {str(ex)}")
            raise  # re-raise the exception
        except Exception as ex:
            logging.error(
                f"An error occurred while getting the database configuration: {str(ex)}"
            )
            raise  # re-raise the exception

    def get_current_database_type(self):
        """
        Returns the currently set database type.
        """
        try:
            logging.debug("Getting the current database type.")  # Debug log
            return self.db_type
        except AttributeError as ex:
            logging.error(
                f"An error occurred while getting the current database type: {str(ex)}"
            )
            raise  # re-raise the exception

    def get_database_config(self):
        """
        Returns the current database configuration.
        """
        try:
            logging.debug("Getting the database configuration.")  # Debug log
            return self.database_config
        except AttributeError as ex:
            logging.error(
                f"An error occurred while getting the database configuration: {str(ex)}"
            )
            raise  # re-raise the exception

    def update_database_config(self, new_config):
        """
        Updates the database configuration with the provided new configuration.

        Parameters:
        - new_config: A dictionary containing the new database configurations to be updated.
        """
        try:
            if isinstance(new_config, dict):
                logging.debug("Updating the database configuration.")  # Debug log
                self.database_config.update(new_config)
            else:
                raise TypeError("new_config must be a dictionary.")
        except AttributeError as ae:
            logging.error(
                f"An error occurred while updating the database configuration: {str(ae)}"
            )
            raise  # re-raise the exception
        except TypeError as te:
            logging.error(te)
            raise  # re-raise the exception

    async def get_session(self):
        """
        Returns an async session object using the SQLAlchemy async engine.

        Returns:
        - An async session object.
        """
        if not self._session:
            try:
                if self._engine:
                    logging.debug("Creating a new session.")  # Debug log
                    async_session = sessionmaker(
                        self._engine, expire_on_commit=False, class_=AsyncSession
                    )
                    self._session = await async_session()
                else:
                    raise AttributeError("Engine is not set.")
            except AttributeError as ae:
                logging.error(f"Failed to create session: {ae}")
                raise  # re-raise the exception
            except Exception as e:
                logging.error(
                    f"An unexpected error occurred while creating the session: {e}"
                )
                raise  # re-raise the exception
        return self._session

    async def close(self):
        """
        Closes the current session.
        """
        try:
            if self._session:
                logging.debug("Closing the session.")  # Debug log
                await self._session.close()
        except Exception as ex:
            logging.error(f"Failed to close session: {ex}")
            raise  # re-raise the exception

    async def __aenter__(self):
        """
        Defines what the context manager should do at the beginning of the block created by the 'with' statement.
        It returns an async session object.
        """
        try:
            logging.debug("Entering the context, getting the session.")  # Debug log
            self._session = await self.get_session()
            return self._session
        except Exception as ex:
            logging.error(f"Failed to enter context: {ex}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Defines what the context manager should do after its block has been executed (or terminates).
        It closes the current session.
        """
        try:
            logging.debug("Exiting the context, closing the session.")  # Debug log
            await self.close()
        except Exception as ex:
            logging.error(f"Failed to exit context: {ex}")
            raise

    async def create_tables(self):
        """
        Creates tables in the database.
        """
        try:
            logging.debug("Creating tables.")  # Debug log

            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Print table names
            async with self._engine.connect() as conn:
                result = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_table_names()
                )
            print(str(result))

        except Exception as ex:
            logging.error(f"Failed to create tables: {ex}")
            raise

    async def get_tables(self):
        """
        Retrieves and returns a list of all table names in the database.

        This function establishes an asynchronous connection with the database,
        then synchronously runs the inspect function to retrieve table names.

        Returns:
        - A list of table names in the database.
        """
        async with self._engine.begin() as conn:
            result = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
        return result
