# -*- coding: utf-8 -*-
from datetime import datetime
from uuid import uuid4

from loguru import logger
from sqlalchemy import Column, DateTime, String, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from src.main import DB as db


class BaseModel:
    """
    A base model class for SQLAlchemy ORM with common columns and methods.

    Attributes:
        id (String): Primary key column with UUID as a string.
        date_created (DateTime): Date and time when the record was created.
        date_updated (DateTime): Date and time when the record was last updated.
    """

    id = Column(String, primary_key=True)
    date_created = Column(DateTime, index=True, default=datetime.utcnow)
    date_updated = Column(
        DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @classmethod
    async def list_all(cls, filters=None, order_by=None, limit=500, offset=0):
        """
        List all instances of the model, optionally filtered, sorted, limited and offset.

        Args:
            filters (dict, optional): A dictionary of filters to apply. Defaults to None.
            order_by (str, optional): A string in the format "column:direction" to sort the results. Defaults to None.
            limit (int, optional): The maximum number of instances to return. Defaults to 100, maxes out at 500.
            offset (int, optional): The number of instances to skip before returning results. Defaults to 0.

        Returns:
            list: A list of instances matching the filters and sorted by the specified order.

        Example:
            users = await User.list_all(filters={"name": "John"}, order_by="date_created:desc", limit=10, offset=20)
        """
        logger.debug(f"Listing all {cls.__name__} objects")
        query = select(cls)

        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if key == "date_created":
                    query = query.where(cls.date_created >= value)
                elif key == "date_updated":
                    query = query.where(cls.date_updated >= value)
                else:
                    query = query.where(getattr(cls, key).like(f"%{value}%"))

        # Apply ordering if provided
        if order_by:
            column, direction = order_by.split(":")
            if direction.lower() == "desc":
                query = query.order_by(desc(getattr(cls, column)))
            else:
                query = query.order_by(getattr(cls, column))

        # Apply limit and offset if provided
        if limit is not None:
            limit = min(limit, 1000)
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        instances = await db.execute(query)
        instances = instances.scalars().all()
        return instances

    @classmethod
    async def count_all(cls, filters=None):
        """
        Count all instances of the model, optionally filtered.

        Args:
            filters (dict, optional): A dictionary of filters to apply. Defaults to None.

        Returns:
            int: The number of instances matching the filters.

        Example:
            count = await User.count_all(filters={"name": "John"})
        """
        logger.debug(f"Counting all {cls.__name__} objects")
        query = select(func.count(cls.id))

        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if key == "date_created":
                    query = query.where(cls.date_created >= value)
                elif key == "date_updated":
                    query = query.where(cls.date_updated >= value)
                else:
                    query = query.where(getattr(cls, key).like(f"%{value}%"))

        count = await db.scalar(query)
        return count

    @classmethod
    async def create(cls, **kwargs):
        """
        Create a new instance of the model and persist it to the database.

        Args:
            **kwargs: Keyword arguments for the model's fields.

        Returns:
            BaseModel: The created instance.

        Raises:
            ValueError: If there is a duplicate value for a unique field.

        Example:
            user = await User.create(name="John Doe", email="john@example.com")
        """
        logger.debug(f"Creating {cls.__name__} with kwargs: {kwargs}")
        instance = cls(id=str(uuid4()), **kwargs)
        db.add(instance)

        try:
            await db.commit()
        except IntegrityError as e:
            logger.exception("Error committing to database")
            await db.rollback()
            raise ValueError("Duplicate value for unique field") from e
        except Exception as e:
            logger.exception("Error committing to database")
            await db.rollback()
            raise
        return instance

    @classmethod
    async def delete(cls, id):
        """
        Delete an instance of the model by its ID.

        Args:
            id (str): The ID of the instance to delete.

        Raises:
            Exception: If there is an error committing to the database.

        Example:
            await User.delete("123e4567-e89b-12d3-a456-426614174000")
        """
        logger.debug(f"Deleting {cls.__name__} with ID {id}")
        query = cls.__table__.delete().where(cls.id == id)
        await db.execute(query)

        try:
            await db.commit()
        except Exception as e:
            logger.exception("Error committing to database")
            await db.rollback()
            raise

    @classmethod
    async def update(cls, id, **kwargs):
        """
        Update an instance of the model by its ID with the provided keyword arguments.

        Args:
            id (str): The ID of the instance to update.
            **kwargs: Keyword arguments for the fields to update.

        Returns:
            BaseModel: The updated instance.

        Example:
            user = await User.update("123e4567-e89b-12d3-a456-426614174000", name="Jane Doe")
        """
        logger.debug(f"Updating {cls.__name__} with ID {id} and kwargs: {kwargs}")
        query = (
            cls.__table__.update()
            .where(cls.id == bindparam("id"))
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )

        # Check if row exists before updating
        instance = await cls.get(id)

        await db.execute(query, {"id": id, **kwargs})
        # No need for try-except block here
        await db.commit()
        return instance

    @classmethod
    async def get_id(cls, id):
        """
        Get an instance of the model by its ID.

        Args:
            id (str): The ID of the instance to retrieve.

        Returns:
            BaseModel: The retrieved instance.

        Example:
            user = await User.get_id("123e4567-e89b-12d3-a456-426614174000")
        """
        logger.debug(f"Retrieving {cls.__name__} with ID {id}")
        query = select(cls).where(cls.id == id)
        instance = await db.execute(query)
        instance = instance.scalars().first()
        return instance
