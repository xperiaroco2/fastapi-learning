from app.schemas.base import BaseResponse


class AnalyseRunResponse(BaseResponse):
    hypothesis: str | None
    action_plan: list[str] | None
    grounded: bool
