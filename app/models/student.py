from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)

    academic_profile: Mapped[str | None] = mapped_column(Text, nullable=True)

    cases: Mapped[list[Case]] = relationship(back_populates="student", lazy="raise")
