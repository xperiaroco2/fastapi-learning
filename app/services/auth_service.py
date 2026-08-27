from collections import namedtuple
from typing import Annotated

import jwt
from core import (
    EntityUnauthorizedError,
    check_password,
    decode_refresh_token,
    encode_access_token,
    encode_refresh_token,
    hash_password,
)
from fastapi import HTTPException
from fastapi.params import Depends
from models import User
from schemas import LoginRequestDTO, RegisterRequestDTO
from services import UserService, get_user_service
from starlette.status import HTTP_401_UNAUTHORIZED

Tokens = namedtuple("tokens", ["access_token", "refresh_token"])


def get_auth_service(user_service: Annotated[UserService, Depends(get_user_service)]) -> AuthService:
    return AuthService(user_service)


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register_user(self, body: RegisterRequestDTO) -> User:
        hashed_password = hash_password(password=body.password)
        new_user = await self.user_service.create_user(body.name, body.email, hashed_password)

        return new_user

    async def login_user(self, body: LoginRequestDTO) -> Tokens:
        user = await self.user_service.find_by_email(email=body.email)
        is_password_valid = check_password(password=body.password, hashed_password=user.password_hash)

        if not is_password_valid:
            raise EntityUnauthorizedError(entity_name="User", field_name="email", field_value=user.email)

        return Tokens(
            access_token=encode_access_token(user_email=user.email),
            refresh_token=encode_refresh_token(user_email=user.email),
        )

    async def renew_access_token(self, refresh_token: str | None = None) -> str:
        if not refresh_token:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

        try:
            payload = decode_refresh_token(refresh_token)

            if not payload or payload.get("type") != "refresh":
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            user_email = payload.get("sub")

            if not user_email:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        except jwt.PyJWTError as err:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Refresh token expired or invalid") from err

        user = await self.user_service.find_by_email(email=user_email)

        if not user:
            raise EntityUnauthorizedError(entity_name="User", field_name="email", field_value=user_email)

        return encode_access_token(user_email)
