from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from datetime import datetime
import os
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import calendar
from webbrowser import open as webbrowser_open
from urllib.parse import quote

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kniha_jizd_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Vytvoření adresáře pro exporty
if not os.path.exists(os.path.join(app.static_folder, 'exports')):
    os.makedirs(os.path.join(app.static_folder, 'exports'), exist_ok=True)

from models import db, Jizda, Tankovani, Vozidlo, User

# Inicializace databáze a login manageru
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Pro přístup k této stránce se musíte přihlásit.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Pro přístup k této stránce musíte být administrátor.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            # Pokud byl dark mode zapnutý před přihlášením, nastavíme ho uživateli
            if session.get('dark_mode', False):
                user.dark_mode = True
                db.session.commit()
            login_user(user, remember=bool(request.form.get('remember')))
            next_page = request.args.get('next')
            flash('Přihlášení bylo úspěšné!', 'success')
            return redirect(next_page or url_for('index'))
        flash('Nesprávné přihlašovací údaje.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if request.form['password'] != request.form['password2']:
            flash('Hesla se neshodují.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=request.form['username']).first():
            flash('Toto uživatelské jméno je již obsazené.', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=request.form['email']).first():
            flash('Tento email je již zaregistrován.', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        
        # První uživatel bude admin
        if User.query.count() == 0:
            user.is_admin = True
            user.max_vozidel = 999  # Neomezený počet vozidel pro admina
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrace byla úspěšná! Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Byli jste úspěšně odhlášeni.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/upravit_uzivatele/<int:id>', methods=['POST'])
@login_required
@admin_required
def upravit_uzivatele(id):
    user = User.query.get_or_404(id)
    user.max_vozidel = int(request.form['max_vozidel'])
    user.is_admin = bool(request.form.get('is_admin'))
    db.session.commit()
    flash('Uživatel byl úspěšně upraven.', 'success')
    return redirect(url_for('admin'))

@app.route('/')
@login_required
def index():
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'warning')
        return redirect(url_for('vozidla'))
    
    aktivni_vozidlo = Vozidlo.query.get(aktivni_vozidlo_id)
    if not aktivni_vozidlo:
        flash('Vybrané vozidlo neexistuje', 'danger')
        return redirect(url_for('vozidla'))
    
    # Načtení jízd pro aktivní vozidlo
    jizdy = Jizda.query.filter_by(vozidlo_id=aktivni_vozidlo.id).order_by(Jizda.datum.desc()).all()
    
    # Načtení tankování pro aktivní vozidlo
    tankovani = Tankovani.query.filter_by(vozidlo_id=aktivni_vozidlo.id).order_by(Tankovani.datum.desc()).all()
    
    # Výpočet celkové spotřeby
    celkem_km = sum(j.pocet_km for j in jizdy) if jizdy else 0
    celkem_litru = sum(t.litru for t in tankovani) if tankovani else 0
    prumerna_spotreba = (celkem_litru / celkem_km * 100) if celkem_km > 0 else 0
    
    vozidla = Vozidlo.query.filter_by(user_id=current_user.id).all()
    
    return render_template('index.html', 
                         jizdy=jizdy, 
                         tankovani=tankovani,
                         aktivni_vozidlo=aktivni_vozidlo,
                         vozidla=vozidla,
                         prumerna_spotreba=prumerna_spotreba)

@app.route('/vozidla')
@login_required
def vozidla():
    vozidla = Vozidlo.query.filter_by(user_id=current_user.id).all()
    return render_template('vozidla.html', vozidla=vozidla, max_vozidel=current_user.max_vozidel)

@app.route('/pridat_vozidlo', methods=['POST'])
@login_required
def pridat_vozidlo():
    nazev = request.form.get('nazev')
    spz = request.form.get('spz')
    poznamka = request.form.get('poznamka')
    pocatecni_stav_km = request.form.get('pocatecni_stav_km', type=int)
    
    if not nazev or not spz or pocatecni_stav_km is None:
        flash('Název, SPZ a počáteční stav tachometru jsou povinné údaje', 'danger')
        return redirect(url_for('vozidla'))
    
    if pocatecni_stav_km < 0:
        flash('Počáteční stav tachometru nemůže být záporný', 'danger')
        return redirect(url_for('vozidla'))
    
    # Kontrola limitu vozidel
    aktualni_pocet = Vozidlo.query.filter_by(user_id=current_user.id).count()
    if aktualni_pocet >= current_user.max_vozidel:
        flash(f'Dosáhli jste maximálního počtu vozidel ({current_user.max_vozidel})', 'danger')
        return redirect(url_for('vozidla'))
    
    vozidlo = Vozidlo(
        nazev=nazev,
        spz=spz,
        poznamka=poznamka,
        pocatecni_stav_km=pocatecni_stav_km,
        aktualni_stav_km=pocatecni_stav_km,
        user_id=current_user.id
    )
    db.session.add(vozidlo)
    try:
        db.session.commit()
        flash('Vozidlo bylo úspěšně přidáno', 'success')
    except:
        db.session.rollback()
        flash('Chyba při ukládání vozidla. SPZ musí být unikátní.', 'danger')
    
    return redirect(url_for('vozidla'))

@app.route('/prepnout_vozidlo/<int:id>')
@login_required
def prepnout_vozidlo(id):
    vozidlo = Vozidlo.query.get_or_404(id)
    session['aktivni_vozidlo_id'] = vozidlo.id
    flash(f'Aktivní vozidlo bylo změněno na: {vozidlo.nazev}', 'success')
    return redirect(url_for('index'))

@app.route('/aktivovat_vozidlo/<int:id>')
@login_required
def aktivovat_vozidlo(id):
    vozidlo = Vozidlo.query.get_or_404(id)
    vozidlo.aktivni = True
    db.session.commit()
    flash(f'Vozidlo {vozidlo.nazev} bylo aktivováno', 'success')
    return redirect(url_for('vozidla'))

@app.route('/deaktivovat_vozidlo/<int:id>')
@login_required
def deaktivovat_vozidlo(id):
    vozidlo = Vozidlo.query.get_or_404(id)
    vozidlo.aktivni = False
    db.session.commit()
    flash(f'Vozidlo {vozidlo.nazev} bylo deaktivováno', 'success')
    return redirect(url_for('vozidla'))

@app.route('/nova_jizda', methods=['GET', 'POST'])
@login_required
def nova_jizda():
    if request.method == 'POST':
        aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
        if not aktivni_vozidlo_id:
            flash('Nejprve vyberte aktivní vozidlo', 'danger')
            return redirect(url_for('vozidla'))
        
        vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
        if vozidlo.user_id != current_user.id:
            flash('Nemáte oprávnění k tomuto vozidlu', 'danger')
            return redirect(url_for('index'))
        
        datum = request.form.get('datum')
        ridic = request.form.get('ridic')
        misto_odjezdu = request.form.get('misto_odjezdu')
        misto_prijezdu = request.form.get('misto_prijezdu')
        pocet_km = request.form.get('pocet_km', type=float)
        ucel_jizdy = request.form.get('ucel_jizdy')
        
        if not all([datum, ridic, misto_odjezdu, misto_prijezdu, pocet_km, ucel_jizdy]):
            flash('Všechna pole jsou povinná', 'danger')
            return redirect(url_for('nova_jizda'))
        
        try:
            datum = datetime.strptime(datum, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Neplatný formát data a času', 'danger')
            return redirect(url_for('nova_jizda'))
        
        if pocet_km <= 0:
            flash('Počet kilometrů musí být větší než 0', 'danger')
            return redirect(url_for('nova_jizda'))
        
        # Výpočet nového stavu tachometru
        novy_stav_tachometru = vozidlo.aktualni_stav_km + int(pocet_km)
        
        jizda = Jizda(
            datum=datum,
            vozidlo_id=aktivni_vozidlo_id,
            ridic=ridic,
            misto_odjezdu=misto_odjezdu,
            misto_prijezdu=misto_prijezdu,
            pocet_km=pocet_km,
            ucel_jizdy=ucel_jizdy,
            stav_tachometru=novy_stav_tachometru
        )
        
        # Aktualizace stavu tachometru vozidla
        vozidlo.aktualni_stav_km = novy_stav_tachometru
        
        db.session.add(jizda)
        try:
            db.session.commit()
            flash('Jízda byla úspěšně přidána', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('Chyba při ukládání jízdy', 'danger')
            return redirect(url_for('nova_jizda'))
    
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    aktivni_vozidlo = None
    if aktivni_vozidlo_id:
        aktivni_vozidlo = Vozidlo.query.get(aktivni_vozidlo_id)
        if aktivni_vozidlo and aktivni_vozidlo.user_id != current_user.id:
            aktivni_vozidlo = None
    
    return render_template('nova_jizda.html', aktivni_vozidlo=aktivni_vozidlo, now=datetime.now())

@app.route('/nove_tankovani', methods=['GET', 'POST'])
@login_required
def nove_tankovani():
    if request.method == 'POST':
        aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
        if not aktivni_vozidlo_id:
            flash('Nejprve vyberte aktivní vozidlo', 'danger')
            return redirect(url_for('vozidla'))

        try:
            stav_tachometru = int(request.form['stav_tachometru'])
            litru = float(request.form['litru'])
            cena_za_litr = float(request.form['cena_za_litr'])
            celkova_cena = litru * cena_za_litr
            
            nove_tankovani = Tankovani(
                datum=datetime.strptime(request.form['datum'], '%Y-%m-%d'),
                vozidlo_id=aktivni_vozidlo_id,
                stav_tachometru=stav_tachometru,
                litru=litru,
                cena_za_litr=cena_za_litr,
                celkova_cena=celkova_cena,
                poznamka=request.form.get('poznamka', '')
            )
            
            db.session.add(nove_tankovani)
            db.session.commit()
            flash('Tankování bylo úspěšně přidáno!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Neplatné hodnoty pro stav tachometru, litry nebo cenu', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Chyba při ukládání tankování: {str(e)}', 'danger')
    
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'danger')
        return redirect(url_for('vozidla'))
        
    aktivni_vozidlo = Vozidlo.query.get(aktivni_vozidlo_id)
    return render_template('nove_tankovani.html', aktivni_vozidlo=aktivni_vozidlo, now=datetime.now())

@app.route('/statistiky')
@login_required
def statistiky():
    vozidla = Vozidlo.query.filter_by(user_id=current_user.id).all()
    statistiky_vozidel = []
    
    for vozidlo in vozidla:
        # Celkový počet kilometrů
        celkem_km = db.session.query(db.func.sum(Jizda.pocet_km)).filter_by(vozidlo_id=vozidlo.id).scalar() or 0
        
        # Celkové náklady na PHM
        celkem_phm = db.session.query(db.func.sum(Tankovani.celkova_cena)).filter_by(vozidlo_id=vozidlo.id).scalar() or 0
        
        # Průměrná spotřeba
        posledni_tankovani = Tankovani.query.filter_by(vozidlo_id=vozidlo.id).order_by(Tankovani.datum.desc()).limit(2).all()
        prumerna_spotreba = None
        if len(posledni_tankovani) >= 2:
            km_mezi = db.session.query(db.func.sum(Jizda.pocet_km)).filter(
                Jizda.vozidlo_id == vozidlo.id,
                Jizda.datum > posledni_tankovani[1].datum,
                Jizda.datum <= posledni_tankovani[0].datum
            ).scalar() or 0
            
            if km_mezi > 0:
                prumerna_spotreba = round((posledni_tankovani[0].litru / km_mezi) * 100, 2)
        
        statistiky_vozidel.append({
            'vozidlo': vozidlo.nazev,
            'spz': vozidlo.spz,
            'celkem_km': round(celkem_km, 1),
            'celkem_phm': round(celkem_phm, 2),
            'prumerna_spotreba': prumerna_spotreba,
            'naklady_na_km': round(celkem_phm / celkem_km, 2) if celkem_km > 0 else 0
        })
    
    return render_template('statistiky.html', statistiky=statistiky_vozidel)

@app.route('/uprava_jizdy/<int:id>', methods=['GET', 'POST'])
@login_required
def uprava_jizdy(id):
    jizda = Jizda.query.get_or_404(id)
    if request.method == 'POST':
        jizda.datum = datetime.strptime(request.form['datum'], '%Y-%m-%d')
        jizda.vozidlo_id = int(request.form['vozidlo_id'])
        jizda.spz = request.form['spz']
        jizda.ridic = request.form['ridic']
        jizda.misto_odjezdu = request.form['misto_odjezdu']
        jizda.misto_prijezdu = request.form['misto_prijezdu']
        jizda.pocet_km = float(request.form['pocet_km'])
        jizda.ucel_jizdy = request.form['ucel_jizdy']
        jizda.stav_tachometru = int(request.form['stav_tachometru'])
        
        db.session.commit()
        flash('Jízda byla úspěšně upravena!', 'success')
        return redirect(url_for('index'))
    return render_template('uprava_jizdy.html', jizda=jizda)

@app.route('/smazat_jizdu/<int:id>')
@login_required
def smazat_jizdu(id):
    jizda = Jizda.query.get_or_404(id)
    db.session.delete(jizda)
    db.session.commit()
    flash('Jízda byla úspěšně smazána!', 'success')
    return redirect(url_for('index'))

@app.route('/api/posledni_stav_tachometru/<spz>')
@login_required
def posledni_stav_tachometru(spz):
    # Nejprve zkusíme najít poslední jízdu
    posledni_jizda = Jizda.query.filter_by(spz=spz).order_by(Jizda.datum.desc()).first()
    
    # Pokud není jízda, zkusíme poslední tankování
    if not posledni_jizda:
        posledni_tankovani = Tankovani.query.filter_by(spz=spz).order_by(Tankovani.datum.desc()).first()
        if posledni_tankovani:
            return jsonify({'stav_tachometru': posledni_tankovani.stav_tachometru})
    else:
        return jsonify({'stav_tachometru': posledni_jizda.stav_tachometru})
    
    return jsonify({'stav_tachometru': None})

@app.route('/upravit_vozidlo/<int:id>', methods=['GET', 'POST'])
@login_required
def upravit_vozidlo(id):
    vozidlo = Vozidlo.query.get_or_404(id)
    if request.method == 'POST':
        vozidlo.nazev = request.form['nazev']
        vozidlo.spz = request.form['spz']
        vozidlo.poznamka = request.form.get('poznamka')
        
        try:
            db.session.commit()
            flash('Vozidlo bylo úspěšně upraveno', 'success')
            return redirect(url_for('vozidla'))
        except:
            db.session.rollback()
            flash('Chyba při ukládání změn', 'danger')
    
    return render_template('upravit_vozidlo.html', vozidlo=vozidlo)

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    if current_user.is_authenticated:
        current_user.dark_mode = not current_user.dark_mode
        db.session.commit()
    else:
        session['dark_mode'] = not session.get('dark_mode', False)
    return jsonify({'success': True})

@app.route('/jizdy_mesic/<int:rok>/<int:mesic>')
@login_required
def jizdy_mesic(rok, mesic):
    # Kontrola platnosti data
    if not (1 <= mesic <= 12 and 2000 <= rok <= 2100):
        flash('Neplatný měsíc nebo rok', 'danger')
        return redirect(url_for('index'))
    
    # Získání prvního a posledního dne v měsíci
    _, posledni_den = calendar.monthrange(rok, mesic)
    zacatek_mesice = datetime(rok, mesic, 1)
    konec_mesice = datetime(rok, mesic, posledni_den, 23, 59, 59)
    
    # Získání aktivního vozidla
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'danger')
        return redirect(url_for('vozidla'))
    
    vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění k tomuto vozidlu', 'danger')
        return redirect(url_for('index'))
    
    # Získání jízd pro dané období
    jizdy = Jizda.query.filter(
        Jizda.vozidlo_id == aktivni_vozidlo_id,
        Jizda.datum >= zacatek_mesice,
        Jizda.datum <= konec_mesice
    ).order_by(Jizda.datum).all()
    
    # Výpočet statistik
    celkem_km = sum(j.pocet_km for j in jizdy)
    pocatecni_stav = jizdy[0].stav_tachometru - jizdy[0].pocet_km if jizdy else vozidlo.pocatecni_stav_km
    konecny_stav = jizdy[-1].stav_tachometru if jizdy else vozidlo.aktualni_stav_km
    
    return render_template(
        'jizdy_mesic.html',
        jizdy=jizdy,
        vozidlo=vozidlo,
        rok=rok,
        mesic=mesic,
        celkem_km=celkem_km,
        pocatecni_stav=pocatecni_stav,
        konecny_stav=konecny_stav
    )

@app.route('/export_pdf/<int:rok>/<int:mesic>')
@login_required
def export_pdf(rok, mesic):
    # Získání dat stejně jako v jizdy_mesic
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'danger')
        return redirect(url_for('vozidla'))
    
    vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění k tomuto vozidlu', 'danger')
        return redirect(url_for('index'))
    
    _, posledni_den = calendar.monthrange(rok, mesic)
    zacatek_mesice = datetime(rok, mesic, 1)
    konec_mesice = datetime(rok, mesic, posledni_den, 23, 59, 59)
    
    jizdy = Jizda.query.filter(
        Jizda.vozidlo_id == aktivni_vozidlo_id,
        Jizda.datum >= zacatek_mesice,
        Jizda.datum <= konec_mesice
    ).order_by(Jizda.datum).all()
    
    # Vytvoření PDF
    nazev_souboru = f'kniha_jizd_{vozidlo.spz}_{rok}_{mesic:02d}.pdf'
    cesta_k_souboru = os.path.join(app.static_folder, 'exports', nazev_souboru)
    os.makedirs(os.path.dirname(cesta_k_souboru), exist_ok=True)
    
    # Registrace fontu
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
    
    doc = SimpleDocTemplate(cesta_k_souboru, pagesize=A4)
    elements = []
    
    # Nadpis
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontName = 'ArialBold'
    heading_style = styles['Heading1']
    heading_style.fontName = 'Arial'
    
    elements.append(Paragraph(f'Kniha jízd - {vozidlo.nazev} ({vozidlo.spz})', title_style))
    elements.append(Paragraph(f'Období: {mesic}/{rok}', heading_style))
    
    # Data pro tabulku
    data = [['Datum', 'Řidič', 'Odkud', 'Kam', 'Km', 'Účel jízdy', 'Stav km']]
    celkem_km = 0
    
    for jizda in jizdy:
        data.append([
            jizda.datum.strftime('%d.%m.%Y %H:%M'),
            jizda.ridic,
            jizda.misto_odjezdu,
            jizda.misto_prijezdu,
            str(jizda.pocet_km),
            jizda.ucel_jizdy,
            str(jizda.stav_tachometru)
        ])
        celkem_km += jizda.pocet_km
    
    # Přidání součtu kilometrů
    data.append(['Celkem', '', '', '', str(celkem_km), '', ''])
    
    # Vytvoření tabulky
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'ArialBold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return send_file(
        cesta_k_souboru,
        as_attachment=True,
        download_name=nazev_souboru,
        mimetype='application/pdf'
    )

@app.route('/odeslat_email/<int:rok>/<int:mesic>')
@login_required
def odeslat_email(rok, mesic):
    # Nejprve vytvoříme PDF
    response = export_pdf(rok, mesic)
    if not isinstance(response, tuple):  # Pokud není chyba
        # Otevřeme výchozího emailového klienta s předvyplněným předmětem a přílohou
        nazev_souboru = response.headers['Content-Disposition'].split('filename=')[1].strip('"')
        cesta_k_souboru = os.path.join(app.static_folder, 'exports', nazev_souboru)
        
        # Vytvoření mailto odkazu
        predmet = quote(f'Kniha jízd - {mesic}/{rok}')
        mailto_url = f'mailto:?subject={predmet}&body=V příloze zasílám knihu jízd.'
        
        # Otevření výchozího emailového klienta
        webbrowser_open(mailto_url)
        
        return redirect(url_for('jizdy_mesic', rok=rok, mesic=mesic))
    
    return response

@app.context_processor
def utility_processor():
    return {'now': datetime.now()}

# Inicializace databáze - vytvoření pouze pokud neexistuje
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
