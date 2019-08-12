"""empty message

Revision ID: e5b40d224531
Revises: 0a1daccf422d
Create Date: 2019-08-12 13:46:55.272474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5b40d224531'
down_revision = '0a1daccf422d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensor_data', sa.Column('actuation_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'sensor_data', 'actuation', ['actuation_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sensor_data', type_='foreignkey')
    op.drop_column('sensor_data', 'actuation_id')
    # ### end Alembic commands ###