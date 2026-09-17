from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status
from fastapi.params import Depends

from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.decision import CreateDecisionRequest, DecisionResponse, RerunDecisionResponse
from app.services.decision import DecisionService, get_decision_service

decision_router = APIRouter(prefix="/decisions", tags=["Decision"])


@decision_router.get("", response_model=list[DecisionResponse])
async def get_decisions(
    current_user: Annotated[User, Depends(get_current_user)],
    decision_service: Annotated[DecisionService, Depends(get_decision_service)],
) -> list[DecisionResponse]:
    decisions = await decision_service.get_all(current_user.id)

    return [DecisionResponse.model_validate(decision) for decision in decisions]


@decision_router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision_by_id(
    current_user: Annotated[User, Depends(get_current_user)],
    decision_service: Annotated[DecisionService, Depends(get_decision_service)],
    decision_id: UUID,
) -> DecisionResponse:
    decision = await decision_service.get_by_id(decision_id, current_user.id)

    return DecisionResponse.model_validate(decision)


@decision_router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    current_user: Annotated[User, Depends(get_current_user)],
    decision_service: Annotated[DecisionService, Depends(get_decision_service)],
    body: CreateDecisionRequest,
) -> DecisionResponse:
    decision = await decision_service.create(body, current_user.id)

    return DecisionResponse.model_validate(decision)


@decision_router.post("/{decision_id}/rerun", response_model=RerunDecisionResponse)
async def rerun_decision(
    current_user: Annotated[User, Depends(get_current_user)],
    decision_service: Annotated[DecisionService, Depends(get_decision_service)],
    decision_id: UUID,
) -> RerunDecisionResponse:
    run_id = await decision_service.rerun(decision_id, current_user.id)

    return RerunDecisionResponse(message="Analysis rerun initiated", run_id=run_id)
