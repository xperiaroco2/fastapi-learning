import re

from pydantic import EmailStr, Field, field_validator

from .base import BaseRequestDTO, BaseResponseDTO
from .user import UserResponseDTO


class RegisterRequestDTO(BaseRequestDTO):
    email: EmailStr
    password: str = Field(
        min_length=8, max_length=64, pattern=r"^[A-Za-z\d@$!%*?&#^_\-\+]+$"
    )
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


class RegisterResponseDTO(BaseResponseDTO):
    message: str
    user: UserResponseDTO
