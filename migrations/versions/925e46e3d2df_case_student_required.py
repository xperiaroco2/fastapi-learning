"""case student required

Revision ID: 925e46e3d2df
Revises: e1af540ad755
Create Date: 2026-09-30 15:51:53.605472

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "925e46e3d2df"
down_revision: str | Sequence[str] | None = "e1af540ad755"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Cases without a student were test data from the reverted "question as a case" idea.
    # analysis_runs.case_id has no ON DELETE CASCADE, so runs go first.
    op.execute("DELETE FROM analysis_runs WHERE case_id IN (SELECT id FROM cases WHERE student_id IS NULL)")
    op.execute("DELETE FROM cases WHERE student_id IS NULL")
    op.alter_column("cases", "student_id", existing_type=sa.UUID(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Deleted studentless cases are not restored.
    op.alter_column("cases", "student_id", existing_type=sa.UUID(), nullable=True)
