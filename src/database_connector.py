# -*- coding: utf-8 -*-
import logging
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.settings import settings


class AsyncDatabase:
    # Initialize engine
    DATABASE_URL = settings.database_uri()
    metadata = MetaData()
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Define base model to produce tables
    Base = declarative_base(metadata=metadata)

    # Create async sessionmaker
    sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @classmethod
    async def create_tables(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(cls.Base.metadata.create_all)
        logging.info("Tables created successfully")

    @asynccontextmanager
    async def get_db_session(self):
        db_session = self.sessionmaker()
        success = False
        try:
            yield db_session
            success = True
        except SQLAlchemyError as e:
            logging.error(f"An error occurred during session: {e}")
            raise
        finally:
            if success:
                await db_session.commit()
                logging.debug("Session committed successfully")
            await db_session.close()
            logging.debug("Session closed successfully")
