from typing import Annotated, NamedTuple

from fastapi.params import Depends

from app.core.exceptions import BaseAuthError, InvalidCredentialsError
from app.core.security import (
    check_password,
    decode_refresh_token,
    encode_access_token,
    encode_refresh_token,
    hash_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.user_service import UserService, get_user_service


class Tokens(NamedTuple):
    access_token: str
    refresh_token: str


def get_auth_service(user_service: Annotated[UserService, Depends(get_user_service)]) -> AuthService:
    return AuthService(user_service)


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register_user(self, body: RegisterRequest) -> User:
        hashed_password = hash_password(password=body.password)
        new_user = await self.user_service.create_user(body.name, body.email, hashed_password)

        return new_user

    async def login_user(self, body: LoginRequest) -> Tokens:
        user = await self.user_service.find_by_email(email=body.email)

        if not user:
            raise InvalidCredentialsError()

        is_password_valid = check_password(password=body.password, hashed_password=user.password_hash)

        if not is_password_valid:
            raise InvalidCredentialsError()

        return Tokens(
            access_token=encode_access_token(user_email=user.email),
            refresh_token=encode_refresh_token(user_email=user.email),
        )

    async def renew_access_token(self, refresh_token: str | None = None) -> str:
        if not refresh_token:
            raise BaseAuthError("Refresh token required")

        payload = decode_refresh_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise BaseAuthError("Invalid token")

        user_email = payload.get("sub")

        if not user_email:
            raise BaseAuthError("Invalid token")

        user = await self.user_service.find_by_email(email=user_email)

        if not user:
            raise BaseAuthError("Invalid token")

        return encode_access_token(user_email)
