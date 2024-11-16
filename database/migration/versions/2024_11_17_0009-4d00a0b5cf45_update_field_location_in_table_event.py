"""Update field location in table event

Revision ID: 4d00a0b5cf45
Revises: d5c944c88941
Create Date: 2024-11-17 00:09:33.630097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d00a0b5cf45'
down_revision: Union[str, None] = 'd5c944c88941'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'location',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('city1', 'city2', 'city3', 'city4', 'city5', name='location'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'location',
               existing_type=sa.Enum('city1', 'city2', 'city3', 'city4', 'city5', name='location'),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###