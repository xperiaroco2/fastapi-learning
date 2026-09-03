from typing import Annotated

from fastapi.params import Depends, Header

from app.core.exceptions import EntityUnauthorizedError
from app.core.logger import logger
from app.core.security import decode_access_token
from app.models.user import User
from app.services.user_service import UserService, get_user_service


async def get_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    guard_error = EntityUnauthorizedError(entity_name="User")

    if authorization is None:
        raise guard_error

    _, token = authorization.split(" ")

    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise guard_error

    email = payload["sub"]
    user = await user_service.find_by_email(email=email)

    if not user:
        raise guard_error

    logger.contextualize(user_id=user.id)

    return user
