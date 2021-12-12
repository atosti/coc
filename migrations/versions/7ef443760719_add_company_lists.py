"""Add company lists

Revision ID: 7ef443760719
Revises: a17f3b04d553
Create Date: 2021-12-12 11:42:46.728142

"""
from alembic import op
import sqlalchemy as sa
from app.models.utils import JSONEncodedDict

# revision identifiers, used by Alembic.
revision = '7ef443760719'
down_revision = 'a17f3b04d553'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_time', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('data', JSONEncodedDict(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_list_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_list'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('list')
    # ### end Alembic commands ###