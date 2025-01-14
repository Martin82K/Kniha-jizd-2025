from app import app, db
from sqlalchemy import Column, Boolean

def add_dark_mode_column():
    with app.app_context():
        # Přidání sloupce dark_mode do tabulky users
        db.engine.execute('ALTER TABLE users ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE')
        print('Sloupec dark_mode byl úspěšně přidán!')

if __name__ == '__main__':
    add_dark_mode_column()
