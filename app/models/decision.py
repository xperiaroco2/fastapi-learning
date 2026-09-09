from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, JSON, DateTime, Enum as SQLEnum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class DecisionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Decision(Base, TimestampMixin):
    __tablename__ = "decisions"

    situation: Mapped[str] = mapped_column(String(255), nullable=False)
    chosen_decision: Mapped[str] = mapped_column(String(255), nullable=False)
    personal_reasoning: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[SQLEnum] = mapped_column(SQLEnum(DecisionStatus), default=DecisionStatus.PENDING, index=True)

    user_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    # latest_run_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey('runs.id'), nullable=True, index=True)

    user: Mapped[User] = relationship(back_populates="decisions")
    runs: Mapped[DecisionAnalysisRun] = relationship(back_populates="decision")

    __table_args__ = (Index("idx_decisions_created_at", "created_at"),)


class DecisionAnalysisRun(Base, TimestampMixin):
    __tablename__ = "decision_runs"

    status: Mapped[SQLEnum] = mapped_column(SQLEnum(DecisionStatus), default=DecisionStatus.PENDING, index=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    result_json: Mapped[JSON] = mapped_column(JSON, nullable=True)
    category_text: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    biases_text: Mapped[list[str]] = mapped_column(ARRAY(String(255)), nullable=False)
    error: Mapped[str] = mapped_column(String(255), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    decision_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("decisions.id"), nullable=False, index=True)

    decision: Mapped[Decision] = relationship(back_populates="runs")

    __table_args__ = (Index("idx_decision_runs_created_at", "created_at"),)
