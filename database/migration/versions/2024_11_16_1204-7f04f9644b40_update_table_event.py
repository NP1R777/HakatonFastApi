"""Update table event

Revision ID: 7f04f9644b40
Revises: 0898e021795b
Create Date: 2024-11-16 12:04:28.955761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7f04f9644b40'
down_revision: Union[str, None] = '0898e021795b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               autoincrement=True)
    op.alter_column('event', 'update_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               autoincrement=True)
    op.alter_column('event', 'location',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('city1', 'city2', 'city3', 'city4', 'city', name='location'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'location',
               existing_type=sa.Enum('city1', 'city2', 'city3', 'city4', 'city', name='location'),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    op.alter_column('event', 'update_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               autoincrement=True)
    op.alter_column('event', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###