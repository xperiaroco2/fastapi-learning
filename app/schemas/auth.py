import re

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseRequest, BaseResponse
from app.schemas.user import UserResponse


class RegisterRequest(BaseRequest):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z\d@$!%*?&#^_\-\+]+$")
    name: str | None = Field(
        min_length=4,
        max_length=40,
        default=None,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        return value


class RegisterResponse(BaseResponse):
    message: str
    user: UserResponse


class LoginRequest(BaseRequest):
    email: EmailStr
    password: str


class LoginResponse(BaseResponse):
    access_token: str


class RefreshSessionResponse(LoginResponse):
    pass
