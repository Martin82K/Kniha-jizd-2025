from app import app, db
from models import User, Vozidlo, Jizda, Tankovani
import sqlite3
from datetime import datetime

def parse_datetime(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return datetime.fromisoformat(dt)
    return dt

def migrate_database():
    # Vytvoření nové databáze s aktualizovaným schématem
    with app.app_context():
        db.create_all()
        
        # Připojení ke staré databázi
        old_conn = sqlite3.connect('kniha_jizd_v2.db')
        old_cur = old_conn.cursor()
        
        try:
            # Migrace uživatelů
            old_cur.execute('SELECT * FROM users')
            users = old_cur.fetchall()
            for user in users:
                new_user = User(
                    id=user[0],
                    username=user[1],
                    prijmeni=user[2],
                    email=user[3],
                    password_hash=user[4],
                    max_vozidel=user[5],
                    created_at=parse_datetime(user[6]),
                    platnost_do=parse_datetime(user[7]),
                    is_admin=bool(user[8]),
                    dark_mode=bool(user[9])
                )
                db.session.add(new_user)
            
            # Migrace vozidel
            old_cur.execute('SELECT * FROM vozidla')
            vozidla = old_cur.fetchall()
            for vozidlo in vozidla:
                new_vozidlo = Vozidlo(
                    id=vozidlo[0],
                    nazev=vozidlo[1],
                    spz=vozidlo[2],
                    aktivni=bool(vozidlo[3]),
                    vytvoreno=parse_datetime(vozidlo[4]),
                    poznamka=vozidlo[5],
                    pocatecni_stav_km=vozidlo[6],
                    aktualni_stav_km=vozidlo[7],
                    user_id=vozidlo[8]
                )
                db.session.add(new_vozidlo)
            
            # Migrace jízd
            old_cur.execute('SELECT * FROM jizdy')
            jizdy = old_cur.fetchall()
            for jizda in jizdy:
                new_jizda = Jizda(
                    id=jizda[0],
                    datum=parse_datetime(jizda[1]),
                    vozidlo_id=jizda[2],
                    ridic=jizda[3],
                    misto_odjezdu=jizda[4],
                    misto_prijezdu=jizda[5],
                    pocet_km=float(jizda[6]),
                    ucel_jizdy=jizda[7],
                    stav_tachometru=jizda[8],
                    typ_jizdy='pracovní'  # Výchozí hodnota pro existující záznamy
                )
                db.session.add(new_jizda)
            
            # Migrace tankování
            old_cur.execute('SELECT * FROM tankovani')
            tankovani = old_cur.fetchall()
            for tank in tankovani:
                new_tank = Tankovani(
                    id=tank[0],
                    datum=parse_datetime(tank[1]),
                    vozidlo_id=tank[2],
                    stav_tachometru=tank[3],
                    litru=float(tank[4]),
                    cena_za_litr=float(tank[5]),
                    celkova_cena=float(tank[6]),
                    poznamka=tank[7]
                )
                db.session.add(new_tank)
            
            # Uložení všech změn
            db.session.commit()
            print("Migrace úspěšně dokončena")
            
        except Exception as e:
            print(f"Chyba při migraci: {str(e)}")
            db.session.rollback()
        finally:
            old_conn.close()

if __name__ == '__main__':
    migrate_database()
