from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas import RegisterRequestDTO, RegisterResponseDTO, UserResponseDTO
from app.services import UserService, get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponseDTO)
async def register_user(
    body: RegisterRequestDTO,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> RegisterResponseDTO:
    user = await user_service.register_user(body)

    return RegisterResponseDTO(
        user=UserResponseDTO.model_validate(user.__dict__),
        message="User registered successfully!",
    )
