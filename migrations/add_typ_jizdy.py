from alembic import op
import sqlalchemy as sa

def upgrade():
    # Přidání sloupce typ_jizdy do tabulky jizdy
    op.add_column('jizdy', sa.Column('typ_jizdy', sa.String(20), nullable=False, server_default='pracovní'))

def downgrade():
    # Odebrání sloupce typ_jizdy z tabulky jizdy
    op.drop_column('jizdy', 'typ_jizdy')
