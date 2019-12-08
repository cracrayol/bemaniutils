"""Add game column to machine.

Revision ID: 3308af0e619f
Revises: 38ad3e2db188
Create Date: 2017-08-17 20:08:27.228540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3308af0e619f'
down_revision = '38ad3e2db188'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('machine', sa.Column('game', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('machine', 'game')
    # ### end Alembic commands ###
