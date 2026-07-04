from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from app.core import get_db
from app.models import User
from app.schemas import RegisterRequestDTO


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, body: RegisterRequestDTO) -> User:
        query = select(User).where(User.email == body.email)
        result = await self.db.execute(query)
        existing_user: User | None = result.scalars().first()

        # logger.info(query)
        # logger.info(result)
        # logger.info(existing_user)

        if existing_user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        new_user = User(name=body.name, email=body.email, password_hash="hash_here")
        # logger.info(new_user)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info("User successfully created!")

        return new_user


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)
