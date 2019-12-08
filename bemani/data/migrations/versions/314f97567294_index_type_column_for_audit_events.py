"""Index type column for audit events.

Revision ID: 314f97567294
Revises: 36b54cc0bd09
Create Date: 2017-04-14 19:25:51.711211

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '314f97567294'
down_revision = '36b54cc0bd09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_audit_type'), 'audit', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_audit_type'), table_name='audit')
    # ### end Alembic commands ###
