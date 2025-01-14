import os
import sys

# Přidání nadřazené složky do PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime, timedelta

def migrate():
    with app.app_context():
        try:
            # Přidání sloupce prijmeni
            db.session.execute('ALTER TABLE users ADD COLUMN prijmeni TEXT')
            print("Sloupec 'prijmeni' přidán")
        except Exception as e:
            print(f"Sloupec 'prijmeni' již existuje nebo chyba: {str(e)}")
        
        try:
            # Nastavení výchozího příjmení podle username
            db.session.execute('UPDATE users SET prijmeni = username WHERE prijmeni IS NULL')
            print("Výchozí příjmení nastavena")
        except Exception as e:
            print(f"Chyba při nastavování příjmení: {str(e)}")
        
        try:
            # Přidání sloupce platnost_do
            db.session.execute('ALTER TABLE users ADD COLUMN platnost_do TIMESTAMP')
            print("Sloupec 'platnost_do' přidán")
        except Exception as e:
            print(f"Sloupec 'platnost_do' již existuje nebo chyba: {str(e)}")
        
        try:
            # Nastavení výchozí platnosti na 1 rok od teď pro všechny uživatele
            platnost = datetime.utcnow() + timedelta(days=365)
            db.session.execute('UPDATE users SET platnost_do = :platnost WHERE platnost_do IS NULL', {'platnost': platnost})
            print("Výchozí platnost nastavena")
        except Exception as e:
            print(f"Chyba při nastavování platnosti: {str(e)}")
        
        try:
            db.session.commit()
            print("Migrace dokončena úspěšně!")
        except Exception as e:
            print(f"Chyba při commitu změn: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
