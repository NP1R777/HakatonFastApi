"""Update table group_event

Revision ID: 575f9121d10a
Revises: 5ed7df6b6db4
Create Date: 2024-11-16 10:03:48.446730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '575f9121d10a'
down_revision: Union[str, None] = '5ed7df6b6db4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('group_event', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               autoincrement=True)
    op.alter_column('group_event', 'update_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               autoincrement=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('group_event', 'update_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               autoincrement=True)
    op.alter_column('group_event', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###