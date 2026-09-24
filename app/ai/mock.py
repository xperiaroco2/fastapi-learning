from uuid import UUID

from app.ai.provider import AIProvider, CaseAnalysisResult


class MockAIProvider(AIProvider):
    async def analyse_case(
        self, description: str, academic_profile: str, run_id: UUID, user_id: UUID
    ) -> CaseAnalysisResult:
        return CaseAnalysisResult(hypothesis="test hypothesis test", action_plan=["step 1", "step 2", "step 3"])
