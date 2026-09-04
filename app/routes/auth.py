from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshSessionResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.services.auth_service import AuthService, get_auth_service

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=RegisterResponse)
async def register_user(
    body: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    user = await auth_service.register_user(body)

    return RegisterResponse(
        user=UserResponse.model_validate(user),
        message="User registered successfully!",
    )


@auth_router.post("/login", response_model=LoginResponse)
async def login_user(
    response: Response,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    access_token, refresh_token = await auth_service.login_user(body)
    jwt_refresh_lifetime_seconds = get_settings().jwt_refresh_lifetime_seconds

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # For dev purpose
        samesite="strict",
        max_age=jwt_refresh_lifetime_seconds,
    )

    return LoginResponse(access_token=access_token)


@auth_router.post("/refresh", response_model=RefreshSessionResponse)
async def refresh_session(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> RefreshSessionResponse:
    access_token = await auth_service.renew_access_token(refresh_token)

    return RefreshSessionResponse(access_token=access_token)


@auth_router.get("/me", response_model=UserResponse)
async def current_user_profile(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)
