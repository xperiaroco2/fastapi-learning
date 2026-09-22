from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, Text, Uuid, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CaseStatus
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.run import AnalysisRun
    from app.models.student import Student
    from app.models.user import User


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CaseStatus] = mapped_column(SQLEnum(CaseStatus), default=CaseStatus.PENDING, index=True)

    teacher_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("students.id"), nullable=False, index=True)
    teacher: Mapped[User] = relationship(back_populates="cases", lazy="raise")
    student: Mapped[Student] = relationship(back_populates="cases", lazy="raise")

    runs: Mapped[list[AnalysisRun]] = relationship(back_populates="case", lazy="raise")
    latest_run: Mapped[AnalysisRun | None] = relationship(
        order_by=desc("analysis_runs.created_at"), viewonly=True, lazy="raise", uselist=False, overlaps="runs"
    )

    __table_args__ = (Index("idx_cases_created_at", "created_at"),)
