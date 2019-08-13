"""empty message

Revision ID: 9c732cedf07c
Revises: cbe9be2d1e4c
Create Date: 2019-08-13 15:59:56.961053

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9c732cedf07c'
down_revision = 'cbe9be2d1e4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('run_summary', 'good_coordination',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('run_summary', 'shaken',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('sensor_data', 'pressure',
               existing_type=mysql.FLOAT(),
               type_=sa.Float(precision='9,5'),
               existing_nullable=True)
    op.alter_column('sensor_data', 'proximity',
               existing_type=mysql.FLOAT(),
               type_=sa.Float(precision='9,5'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sensor_data', 'proximity',
               existing_type=sa.Float(precision='9,5'),
               type_=mysql.FLOAT(),
               existing_nullable=True)
    op.alter_column('sensor_data', 'pressure',
               existing_type=sa.Float(precision='9,5'),
               type_=mysql.FLOAT(),
               existing_nullable=True)
    op.alter_column('run_summary', 'shaken',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('run_summary', 'good_coordination',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    # ### end Alembic commands ###