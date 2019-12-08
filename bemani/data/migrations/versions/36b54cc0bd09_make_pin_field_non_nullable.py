"""Make pin field non-nullable.

Revision ID: 36b54cc0bd09
Revises: b86fe18bfbd3
Create Date: 2017-04-14 18:02:47.780985

"""
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36b54cc0bd09'
down_revision = 'b86fe18bfbd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arcade', 'pin',
               existing_type=mysql.VARCHAR(length=8),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('arcade', 'pin',
               existing_type=mysql.VARCHAR(length=8),
               nullable=True)
    # ### end Alembic commands ###
