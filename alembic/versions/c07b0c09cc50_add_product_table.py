"""add product table

Revision ID: c07b0c09cc50
Revises: 89f590e49f79
Create Date: 2022-08-17 15:03:13.409952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c07b0c09cc50'
down_revision = '89f590e49f79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('desc', sa.String(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)
    op.create_index(op.f('ix_product_name'), 'product', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_name'), table_name='product')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    # ### end Alembic commands ###
