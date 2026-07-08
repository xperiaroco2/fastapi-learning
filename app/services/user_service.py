from typing import Annotated

from fastapi.params import Depends
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import EntityAlreadyExistsError, get_db
from app.models import User
from app.schemas import RegisterRequestDTO


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, body: RegisterRequestDTO) -> User:
        new_user = User(name=body.name, email=body.email, password_hash="hash_here")
        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)

            logger.info(f"User {new_user.email} successfully created!")

            return new_user
        except IntegrityError as err:
            await self.db.rollback()

            logger.warning(f"Registration failed: email {body.email} already exists.")

            raise EntityAlreadyExistsError(
                entity_name="User", field_name="email", field_value=body.email
            ) from err


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)
