from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status
from fastapi.params import Depends

from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.case import CaseResponse, CreateCaseRequest, RerunCaseResponse
from app.services.case import CaseService, get_case_service

case_router = APIRouter(prefix="/cases", tags=["Case"])


@case_router.get("", response_model=list[CaseResponse])
async def get_cases(
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
) -> list[CaseResponse]:
    cases = await case_service.get_all(current_user.id)

    return [CaseResponse.model_validate(case) for case in cases]


@case_router.get("/{case_id}", response_model=CaseResponse)
async def get_case_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
    case_id: UUID,
) -> CaseResponse:
    case = await case_service.get_by_id(case_id, current_user.id)

    return CaseResponse.model_validate(case)


@case_router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
    body: CreateCaseRequest,
) -> CaseResponse:
    case = await case_service.create(body, current_user.id)

    return CaseResponse.model_validate(case)


@case_router.post("/{case_id}/rerun", response_model=RerunCaseResponse)
async def rerun_case(
    current_user: Annotated[User, Depends(get_current_user)],
    case_service: Annotated[CaseService, Depends(get_case_service)],
    case_id: UUID,
) -> RerunCaseResponse:
    run_id = await case_service.rerun(case_id, current_user.id)

    return RerunCaseResponse(message="Analysis rerun initiated", run_id=run_id)
