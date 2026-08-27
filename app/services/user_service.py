from typing import Annotated

from core import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from fastapi.params import Depends
from loguru import logger
from models import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, name: str | None, email: str, password_hash: str) -> User:
        new_user = User(name=name, email=email, password_hash=password_hash)
        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)

            logger.info(f"User {new_user.email} successfully created!")

            return new_user
        except IntegrityError as err:
            await self.db.rollback()

            logger.warning(f"Registration failed: email {email} already exists.")

            raise EntityAlreadyExistsError(entity_name="User", field_name="email", field_value=email) from err

    async def find_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        result = await self.db.scalars(stmt)

        try:
            user = result.one()

            return user
        except NoResultFound as err:
            await self.db.rollback()

            logger.warning(f"User with email {email} not found.")

            raise EntityNotFoundError(entity_name="User", entity_field="email", entity_value=email) from err
