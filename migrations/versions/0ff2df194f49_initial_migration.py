"""initial migration

Revision ID: 0ff2df194f49
Revises: 
Create Date: 2021-12-09 11:39:37.754339

"""
from alembic import op
import sqlalchemy as sa
from app.models.utils import JSONEncodedDict


# revision identifiers, used by Alembic.
revision = '0ff2df194f49'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_time', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('symbol', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_company'))
    )
    op.create_table('snapshot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_time', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('data', JSONEncodedDict(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name=op.f('fk_snapshot_company_id_company')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_snapshot'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('snapshot')
    op.drop_table('company')
    # ### end Alembic commands ###