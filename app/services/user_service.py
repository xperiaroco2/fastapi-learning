from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import EntityAlreadyExistsError
from app.core.logger import logger
from app.models.user import User


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

            logger.info("user_created", email=new_user.email)

            return new_user
        except IntegrityError as err:
            await self.db.rollback()

            logger.warning("registration_failed", reason="already_exists", email=new_user.email)

            raise EntityAlreadyExistsError(entity_name="User", field_name="email", field_value=email) from err

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.scalars(stmt)

        user = result.one_or_none()

        if not user:
            logger.debug("user_not_found", email=email)

        return user
