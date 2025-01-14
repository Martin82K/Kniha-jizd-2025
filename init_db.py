import os
from app import app, db

def init_db():
    with app.app_context():
        # Smazání staré databáze
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kniha_jizd.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Stará databáze smazána: {db_path}")
        
        # Vytvoření nové databáze
        db.create_all()
        print("Nová databáze vytvořena")

if __name__ == '__main__':
    init_db()
