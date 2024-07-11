"""create task table

Revision ID: 0ec284cc86d8
Revises: efa7f31234e1
Create Date: 2024-07-12 01:15:51.147577

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = "0ec284cc86d8"
down_revision: Union[str, None] = "efa7f31234e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tasks",
        sa.Column("name", sa.String(length=70), nullable=False),
        sa.Column("description", sa.String(length=360), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=True),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("scheduled_hours", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(), server_default="Planned", nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###

    op.execute(
        text(
            """
            CREATE TRIGGER last_update_trigger
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_last_update_column();
            """
        )
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tasks")
    # ### end Alembic commands ###

    op.execute(
        text(
            """
            DROP TRIGGER IF EXISTS last_update_trigger ON tasks;
            """
        )
    )
