"""Añade  reset_password_token reset_password_expiration

Revision ID: 7cc3d9e54afd
Revises: 14762a8840c7
Create Date: 2023-10-19 22:59:45.675729

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7cc3d9e54afd'
down_revision = '14762a8840c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_password_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reset_password_expiration', sa.DateTime(), nullable=True))
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=100),
               nullable=False)
        batch_op.create_unique_constraint(None, ['reset_password_token'])
        batch_op.create_unique_constraint(None, ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)
        batch_op.drop_column('reset_password_expiration')
        batch_op.drop_column('reset_password_token')

    # ### end Alembic commands ###
