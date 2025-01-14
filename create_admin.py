from datetime import datetime, timedelta
from models import db, User
from app import app

def create_admin():
    with app.app_context():
        # Kontrola, zda admin již existuje
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # Pokud admin existuje, změníme mu heslo
            admin.set_password('admin')
            db.session.commit()
            print("Heslo admin uživatele bylo změněno na 'admin'")
            return
        
        # Vytvoření nového admin uživatele
        admin = User(
            username='admin',
            prijmeni='Administrator',
            email='admin@example.com',
            platnost_do=datetime.utcnow() + timedelta(days=3650),  # platnost 10 let
            is_admin=True,
            max_vozidel=999
        )
        admin.set_password('admin')
        
        # Uložení do databáze
        db.session.add(admin)
        db.session.commit()
        print("Admin uživatel byl úspěšně vytvořen s heslem 'admin'")

if __name__ == '__main__':
    create_admin()
