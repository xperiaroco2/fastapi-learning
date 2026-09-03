import uuid

from app.schemas.base import BaseResponse


class UserResponse(BaseResponse):
    id: uuid.UUID
    name: str | None
    email: str
