import uuid

from .base import BaseResponseDTO


class UserResponseDTO(BaseResponseDTO):
    id: uuid.UUID
    name: str | None
    email: str
