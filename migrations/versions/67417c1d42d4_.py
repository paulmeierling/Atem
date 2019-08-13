"""empty message

Revision ID: 67417c1d42d4
Revises: 233e57f3aebe
Create Date: 2019-08-13 14:47:20.520060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67417c1d42d4'
down_revision = '233e57f3aebe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('run_summary', sa.Column('good_coordinatioon', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_run_summary_good_coordinatioon'), 'run_summary', ['good_coordinatioon'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_run_summary_good_coordinatioon'), table_name='run_summary')
    op.drop_column('run_summary', 'good_coordinatioon')
    # ### end Alembic commands ###