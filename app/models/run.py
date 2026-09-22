from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, Uuid, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CaseStatus
from app.models import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


class AnalysisRun(Base, TimestampMixin):
    __tablename__ = "analysis_runs"

    hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_plan: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)
    grounded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.PENDING, index=True)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("cases.id"), nullable=False, index=True)
    case: Mapped[Case] = relationship(back_populates="runs", lazy="raise")

    __table_args__ = (Index("idx_case_runs_created_at", "case_id", desc("created_at")),)
