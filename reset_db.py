from app import app, db
import os

def reset_database():
    with app.app_context():
        # Smazání staré databáze
        if os.path.exists('kniha_jizd.db'):
            os.remove('kniha_jizd.db')
            print('Stará databáze byla smazána')
        
        # Vytvoření nové databáze
        db.create_all()
        print('Nová databáze byla vytvořena')

if __name__ == '__main__':
    reset_database()
