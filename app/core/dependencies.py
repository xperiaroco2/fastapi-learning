from collections.abc import AsyncGenerator
from typing import Annotated

from app.core.exceptions import UnauthenticatedError
from app.core.logger import logger
from app.core.security import decode_access_token
from app.models.user import User
from app.services.user_service import UserService, get_user_service
from fastapi.params import Depends, Header


async def get_current_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        authorization: Annotated[str | None, Header()] = None,
) -> AsyncGenerator[User]:
    guard_error = UnauthenticatedError()

    if authorization is None:
        raise guard_error

    try:
        scheme, token = authorization.split(" ", 1)

        if scheme.lower() != "bearer":
            raise ValueError
    except ValueError as err:
        raise guard_error from err

    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise guard_error

    email = payload["sub"]
    user = await user_service.find_by_email(email=email)

    if not user:
        raise guard_error

    with logger.contextualize(user_id=str(user.id)):
        yield user
