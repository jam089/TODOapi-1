"""add name and b_date to user table

Revision ID: d21204238804
Revises: 0ec284cc86d8
Create Date: 2024-07-12 12:31:04.533009

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d21204238804"
down_revision: str | None = "0ec284cc86d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("b_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "b_date")
    op.drop_column("users", "name")
