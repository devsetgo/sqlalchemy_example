# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String

from src.database_functions import Base
# from service.core.demo_user_generator import demo_creator
# from service.database.common_schema import BaseModel
# from service.database.db_session import Base, db

# from src.base_schema import BaseModel


class BaseModel:
    id = Column(String, primary_key=True)
    date_created = Column(DateTime, index=True, default=datetime.utcnow)
    date_updated = Column(
        DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    date_created = Column(DateTime, index=True, default=datetime.utcnow)
    date_updated = Column(
        DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user_name = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(150), unique=True, index=True)
    notes = Column(String(5000))
    password = Column(String(50), index=True)
    is_active = Column(Boolean, default=False, index=True)
    is_approved = Column(Boolean, default=False, index=True)
    is_admin = Column(Boolean, default=False, index=True)

    # @hybrid_property
    # def full_name(self):
    #     return f"{self.first_name} {self.last_name}"

    # def __repr__(self):
    #     return (
    #         f"<{self.__class__.__name__}("
    #         f"id={self.id}, "
    #         f"first_name='{self.first_name}', "
    #         f"last_name='{self.last_name}'"
    #         f")>"
    #     )

    # @classmethod
    # async def create_demo_user_data(cls, num_instances=100):
    #     from tqdm import tqdm

    #     # Check if there are any existing users in the database
    #     filters = {"is_admin": False}
    #     existing_users = await cls.list_all(filters=filters)
    #     if existing_users:
    #         logging.warning(
    #             "Demo data creation aborted. User table already has existing data."
    #         )
    #         return

    #     demo_users = demo_creator(num_instances)
    #     for values in tqdm(demo_users):
    #         # Create a new instance of the cls class with the generated values
    #         instance = cls(id=str(uuid4()), **values)
    #         db.add(instance)

    #         try:
    #             await db.commit()
    #         except Exception as e:
    #             logging.error("Error committing demo data to database")
    #             await db.rollback()
    #             raise SQLAlchemyError(str(e))
