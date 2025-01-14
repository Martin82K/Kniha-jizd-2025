from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, Text, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    prijmeni = db.Column(String(80), nullable=False)  # Nové pole pro příjmení
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(128))
    max_vozidel = db.Column(Integer, default=1)  # Maximální počet vozidel
    created_at = db.Column(DateTime, default=datetime.utcnow)
    platnost_do = db.Column(DateTime, nullable=False)  # Nové pole pro platnost účtu
    is_admin = db.Column(Boolean, default=False)
    dark_mode = db.Column(Boolean, default=True)  # Preference dark mode
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_account_valid(self):
        return datetime.utcnow() <= self.platnost_do

class Vozidlo(db.Model):
    __tablename__ = 'vozidla'
    id = db.Column(Integer, primary_key=True)
    nazev = db.Column(String(100), nullable=False)
    spz = db.Column(String(20), nullable=False, unique=True)
    aktivni = db.Column(Boolean, default=True)
    vytvoreno = db.Column(DateTime, default=datetime.utcnow)
    poznamka = db.Column(Text)
    pocatecni_stav_km = db.Column(Integer, nullable=False)  # Počáteční stav tachometru
    aktualni_stav_km = db.Column(Integer, nullable=False)   # Aktuální stav tachometru
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('vozidla', lazy=True))

class Jizda(db.Model):
    __tablename__ = 'jizdy'
    id = db.Column(Integer, primary_key=True)
    datum = db.Column(DateTime, nullable=False)
    vozidlo_id = db.Column(Integer, db.ForeignKey('vozidla.id'), nullable=False)
    vozidlo = db.relationship('Vozidlo', backref=db.backref('jizdy', lazy=True))
    ridic = db.Column(String(100), nullable=False)
    misto_odjezdu = db.Column(String(200), nullable=False)
    misto_prijezdu = db.Column(String(200), nullable=False)
    pocet_km = db.Column(Float, nullable=False)
    ucel_jizdy = db.Column(String(200), nullable=False)
    stav_tachometru = db.Column(Integer, nullable=False)
    typ_jizdy = db.Column(String(20), nullable=False, default='pracovní')  # Nový sloupec pro typ jízdy

class Tankovani(db.Model):
    __tablename__ = 'tankovani'
    id = db.Column(Integer, primary_key=True)
    datum = db.Column(DateTime, nullable=False)
    vozidlo_id = db.Column(Integer, db.ForeignKey('vozidla.id'), nullable=False)
    vozidlo = db.relationship('Vozidlo', backref=db.backref('tankovani', lazy=True))
    stav_tachometru = db.Column(Integer, nullable=False)
    litru = db.Column(Float, nullable=False)
    cena_za_litr = db.Column(Float, nullable=False)
    celkova_cena = db.Column(Float, nullable=False)
    poznamka = db.Column(Text)
