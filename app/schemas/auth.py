from .base import BaseRequestDTO, BaseResponseDTO
from .user import UserResponseDTO


class RegisterRequestDTO(BaseRequestDTO):
    email: str
    password: str
    name: str | None


class RegisterResponseDTO(BaseResponseDTO):
    message: str
    user: UserResponseDTO
