from typing import Annotated

from core import get_settings
from fastapi import APIRouter, Cookie, Depends, Response
from schemas import LoginRequestDTO, LoginResponseDTO, RefreshSessionResponseDTO
from services import AuthService, get_auth_service

from app.schemas import RegisterRequestDTO, RegisterResponseDTO, UserResponseDTO

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponseDTO)
async def register_user(
    body: RegisterRequestDTO,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponseDTO:
    user = await auth_service.register_user(body)

    return RegisterResponseDTO(
        user=UserResponseDTO.model_validate(user.__dict__),
        message="User registered successfully!",
    )


@router.post("/login", response_model=LoginResponseDTO)
async def login_user(
    response: Response,
    body: LoginRequestDTO,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponseDTO:
    access_token, refresh_token = await auth_service.login_user(body)
    jwt_refresh_lifetime_seconds = get_settings().jwt_refresh_lifetime_seconds

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=jwt_refresh_lifetime_seconds,
    )

    return LoginResponseDTO(access_token=access_token)


@router.post("/refresh", response_model=RefreshSessionResponseDTO)
async def refresh_session(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> RefreshSessionResponseDTO:
    access_token = await auth_service.renew_access_token(refresh_token)

    return RefreshSessionResponseDTO(access_token=access_token)
