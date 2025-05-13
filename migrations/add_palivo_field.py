import os
import sys

# Přidání nadřazené složky do PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Přidání sloupce palivo do tabulky vozidla
            db.session.execute(text('ALTER TABLE vozidla ADD COLUMN palivo TEXT'))
            print("Sloupec 'palivo' přidán do tabulky vozidla")
            db.session.commit()
            print("Migrace dokončena úspěšně!")
        except Exception as e:
            print(f"Chyba při migraci: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
