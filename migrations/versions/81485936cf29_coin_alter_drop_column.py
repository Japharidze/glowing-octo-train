"""Coin alter drop column

Revision ID: 81485936cf29
Revises: 5373bf75104f
Create Date: 2022-01-06 18:01:12.046711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81485936cf29'
down_revision = '5373bf75104f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coins', schema=None) as batch_op:
        batch_op.create_unique_constraint('kucoin_name_uniq', ['kucoin_name'])
        batch_op.drop_column('is_bought')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coins', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_bought', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('kucoin_name_uniq', type_='unique')

    # ### end Alembic commands ###
