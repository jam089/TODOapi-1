"""add role field to user

Revision ID: 7bad295bb257
Revises: d21204238804
Create Date: 2024-07-22 01:59:26.082276

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7bad295bb257"
down_revision: Union[str, None] = "d21204238804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(), server_default="User", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
