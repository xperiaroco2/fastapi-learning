from uuid import UUID

from app.ai.chat.abc import AIChat, CaseAnalysisResult


class MockAIChat(AIChat):
    async def analyse_case(
        self, description: str, academic_profile: str, run_id: UUID, user_id: UUID, documents_info: list[str]
    ) -> CaseAnalysisResult:
        return CaseAnalysisResult(hypothesis="test hypothesis test", action_plan=["step 1", "step 2", "step 3"])
