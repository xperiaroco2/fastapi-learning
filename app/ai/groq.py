from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.ai.helpers import handle_llm_errors
from app.ai.prompts import case_analysis_prompt
from app.ai.provider import AIProvider, CaseAnalysisResult


class GroqAIProvider(AIProvider):
    def __init__(self, api_key: SecretStr, model: str):
        self.llm = ChatGroq(api_key=api_key, model=model, temperature=0.3)

    @handle_llm_errors
    async def analyse_case(
        self, description: str, academic_profile: str, run_id: UUID, user_id: UUID
    ) -> CaseAnalysisResult:
        config: RunnableConfig = {
            "metadata": {
                "run_id": str(run_id),
                "user_id": str(user_id),
            },
            "tags": ["case_analysis"],
        }

        prompt = ChatPromptTemplate.from_messages(
            [("system", case_analysis_prompt.system), ("user", case_analysis_prompt.user)]
        )

        chain = prompt | self.llm.with_structured_output(CaseAnalysisResult)

        result = await chain.ainvoke(
            {
                "description": description,
                "academic_profile": academic_profile,
            },
            config=config,
        )

        return CaseAnalysisResult.model_validate(result)
