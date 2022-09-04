"""empty message

Revision ID: 9632d522e89d
Revises: 7ef443760719
Create Date: 2022-08-14 15:40:40.505309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9632d522e89d'
down_revision = '7ef443760719'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('snapshot_failure',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_time', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('symbol', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_snapshot_failure'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('snapshot_failure')
    # ### end Alembic commands ###