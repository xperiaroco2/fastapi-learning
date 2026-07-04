import uuid

from pydantic import BaseModel


class UserResponseDTO(BaseModel):
    id: uuid.UUID
    name: str | None
    email: str
