from app import app, db
from models import User

def create_admin():
    with app.app_context():
        # Kontrola, zda admin účet již neexistuje
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin účet již existuje!')
            return
        
        # Vytvoření admin účtu
        admin = User(
            username='admin',
            email='admin@example.com',
            max_vozidel=999,  # Neomezený počet vozidel
            is_admin=True
        )
        admin.set_password('admin')
        
        db.session.add(admin)
        db.session.commit()
        print('Admin účet byl úspěšně vytvořen!')

if __name__ == '__main__':
    create_admin()
