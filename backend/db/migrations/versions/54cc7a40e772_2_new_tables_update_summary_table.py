"""2 new tables, update summary table

Revision ID: 54cc7a40e772
Revises: 76124c76d7a7
Create Date: 2024-02-13 00:39:25.799558

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '54cc7a40e772'
down_revision = '76124c76d7a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configuration',
    sa.Column('configuration_id', sa.Integer(), nullable=False),
    sa.Column('tax_rate', sa.Float(), nullable=False),
    sa.Column('hard_cut', sa.Float(), nullable=False),
    sa.Column('soft_cut', sa.Float(), nullable=False),
    sa.Column('added_fees', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('configuration_id')
    )
    op.create_table('items',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('size', sa.String(length=50), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('count_in', sa.Integer(), nullable=True),
    sa.Column('count_out', sa.Integer(), nullable=True),
    sa.Column('comps', sa.Integer(), nullable=True),
    sa.Column('item_type', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_table('sales_summary',
    sa.Column('summary_id', sa.Integer(), nullable=False),
    sa.Column('total_gross', sa.Float(), nullable=True),
    sa.Column('soft_gross', sa.Float(), nullable=True),
    sa.Column('hard_gross', sa.Float(), nullable=True),
    sa.Column('soft_owed', sa.Float(), nullable=True),
    sa.Column('hard_owed', sa.Float(), nullable=True),
    sa.Column('house_due', sa.Float(), nullable=True),
    sa.Column('artist_revenue', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('summary_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('auth0_id', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('auth0_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('credit_card_info',
    sa.Column('cc_info_id', sa.Integer(), nullable=False),
    sa.Column('sales_summary_id', sa.Integer(), nullable=True),
    sa.Column('cc_fee', sa.Float(), nullable=False),
    sa.Column('cc_percentage', sa.Float(), nullable=True),
    sa.Column('cc_sales', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['sales_summary_id'], ['sales_summary.summary_id'], ),
    sa.PrimaryKeyConstraint('cc_info_id')
    )
    op.drop_table('inventory_item')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('auth0_id')
        batch_op.drop_index('email')
        batch_op.drop_index('username')

    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('auth0_id', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.create_index('auth0_id', ['auth0_id'], unique=True)

    op.create_table('inventory_item',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('size', mysql.ENUM('XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '4XL', '5XL', '6XL'), nullable=True),
    sa.Column('price', mysql.FLOAT(), nullable=True),
    sa.Column('count_in', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('count_out', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('comps', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('item_type', mysql.ENUM('Soft', 'Hard'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('credit_card_info')
    op.drop_table('users')
    op.drop_table('sales_summary')
    op.drop_table('items')
    op.drop_table('configuration')
    # ### end Alembic commands ###
