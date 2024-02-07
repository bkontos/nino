"""Update ENUM values in InventoryItem

Revision ID: 76124c76d7a7
Revises: 24a5c55b7244
Create Date: 2024-02-07 22:16:45.033016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76124c76d7a7'
down_revision = '24a5c55b7244'
branch_labels = None
depends_on = None


def upgrade():
# Adjusting the ENUM values for 'size'
    op.execute("ALTER TABLE inventory_item MODIFY COLUMN size ENUM('XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '4XL', '5XL', '6XL')")

    # Adjusting the ENUM values for 'item_type'
    op.execute("ALTER TABLE inventory_item MODIFY COLUMN item_type ENUM('Soft', 'Hard')")


def downgrade():
    # Revert 'size' ENUM changes back to original
    op.execute("ALTER TABLE inventory_item MODIFY COLUMN size ENUM('XS', 'small', 'medium', 'large', 'XL', 'XXL', 'XXXL', '4X', '5XL', '6XL')")

    # Revert 'item_type' ENUM changes back to original
    op.execute("ALTER TABLE inventory_item MODIFY COLUMN item_type ENUM('soft', 'hard')")
