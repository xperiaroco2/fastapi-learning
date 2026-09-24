from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel, Field


class CaseAnalysisResult(BaseModel):
    hypothesis: str = Field(min_length=20, max_length=1000)
    action_plan: list[str] = Field(min_length=3, max_length=5)
    grounded: bool = Field(default=False)


class AIProvider(ABC):
    @abstractmethod
    async def analyse_case(
        self, description: str, academic_profile: str, run_id: UUID, user_id: UUID
    ) -> CaseAnalysisResult:
        pass
