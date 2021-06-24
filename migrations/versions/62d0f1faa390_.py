"""empty message

Revision ID: 62d0f1faa390
Revises: ae4f25344788
Create Date: 2021-06-24 22:24:26.355645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62d0f1faa390'
down_revision = 'ae4f25344788'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tables', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tables', sa.Column('date', sa.VARCHAR(length=100), nullable=True))
    # ### end Alembic commands ###
