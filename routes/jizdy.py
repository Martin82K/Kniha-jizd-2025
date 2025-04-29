from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import db, Jizda, Vozidlo, Tankovani
from forms.jizdy_forms import JizdaForm

jizdy_bp = Blueprint('jizdy', __name__)

@jizdy_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    aktivni_vozidlo = None
    if aktivni_vozidlo_id:
        aktivni_vozidlo = Vozidlo.query.get(aktivni_vozidlo_id)
        print('DEBUG: aktivni_vozidlo_id:', aktivni_vozidlo_id)
        print('DEBUG: aktivni_vozidlo:', aktivni_vozidlo)
        # Zobrazit pouze jízdy, které patří aktivnímu vozidlu a zároveň uživateli
        jizdy = Jizda.query.join(Vozidlo).filter(
            Jizda.vozidlo_id == aktivni_vozidlo_id,
            Vozidlo.user_id == current_user.id
        ).order_by(Jizda.datum.desc()).paginate(page=page, per_page=per_page)
        print('DEBUG: jizdy.items:', jizdy.items)
    else:
        vozidla_uzivatele = Vozidlo.query.filter_by(user_id=current_user.id).all()
        vozidlo_ids = [v.id for v in vozidla_uzivatele]
        print('DEBUG: vozidlo_ids:', vozidlo_ids)
        jizdy = Jizda.query.filter(Jizda.vozidlo_id.in_(vozidlo_ids)).order_by(Jizda.datum.desc()).paginate(page=page, per_page=per_page)
        print('DEBUG: jizdy.items:', jizdy.items)
    if aktivni_vozidlo_id:
        tankovani = aktivni_vozidlo.tankovani.order_by(Tankovani.datum.desc()).limit(5).all()
    else:
        tankovani = Tankovani.query.order_by(Tankovani.datum.desc()).limit(5).all()
    return render_template('index.html', jizdy=jizdy, aktivni_vozidlo=aktivni_vozidlo, tankovani=tankovani)

@jizdy_bp.route('/nova_jizda', methods=['GET', 'POST'])
@login_required
def nova_jizda():
    from datetime import datetime
    now = datetime.now()  # Vytvoření aktuálního data a času
    
    form = JizdaForm()
    form.ridic.data = current_user.prijmeni
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
    # Výpočet aktuálního stavu tachometru
    posledni_jizda = Jizda.query.filter_by(vozidlo_id=aktivni_vozidlo_id).order_by(Jizda.datum.desc()).first()
    if posledni_jizda:
        predvyplneny_stav = posledni_jizda.stav_tachometru
    else:
        predvyplneny_stav = vozidlo.pocatecni_stav_km
    
    # Nastavení hodnoty stav_tachometru
    if hasattr(form, 'stav_tachometru'):
        form.stav_tachometru.data = predvyplneny_stav
    
    if request.method == 'POST':
        print('POST data:', request.form)
        print('form.datum.data:', form.datum.data)
        print('form.errors:', form.errors)
        print('form.csrf_token.errors:', form.csrf_token.errors)
    
    if form.validate_on_submit():
        datum_dt = datetime.combine(form.datum.data, datetime.min.time()) if form.datum.data else None
        pocet_km = form.pocet_km.data
        novy_stav_tachometru = predvyplneny_stav + pocet_km if pocet_km else predvyplneny_stav
        
        # Aktualizace stavu tachometru vozidla
        vozidlo.aktualni_stav_km = novy_stav_tachometru
        
        jizda = Jizda(
            datum=datum_dt,
            vozidlo_id=aktivni_vozidlo_id,
            ridic=form.ridic.data,
            misto_odjezdu=form.misto_odjezdu.data,
            misto_prijezdu=form.misto_prijezdu.data,
            pocet_km=form.pocet_km.data,
            ucel_jizdy=form.ucel_jizdy.data,
            stav_tachometru=novy_stav_tachometru,
            typ_jizdy=form.typ_jizdy.data
        )
        db.session.add(jizda)
        db.session.commit()
        flash('Jízda byla úspěšně přidána!', 'success')
        return redirect(url_for('jizdy.index'))
    
    return render_template('nova_jizda.html', form=form, aktivni_vozidlo=vozidlo, now=now)

@jizdy_bp.route('/edit_jizda/<int:jizda_id>', methods=['GET', 'POST'])
@login_required
def edit_jizda(jizda_id):
    jizda = Jizda.query.get_or_404(jizda_id)
    # Kontrola, zda jízda patří k vozidlu uživatele
    vozidlo = Vozidlo.query.get(jizda.vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění k úpravě této jízdy.', 'danger')
        return redirect(url_for('jizdy.index'))
    
    form = JizdaForm(obj=jizda)
    if form.validate_on_submit():
        from datetime import datetime
        datum_dt = datetime.combine(form.datum.data, datetime.min.time()) if form.datum.data else None
        form.populate_obj(jizda)
        jizda.datum = datum_dt
        db.session.commit()
        flash('Jízda byla upravena.', 'success')
        return redirect(url_for('jizdy.index'))
    return render_template('edit_jizda.html', form=form, jizda=jizda)

@jizdy_bp.route('/delete_jizda/<int:jizda_id>', methods=['POST'])
@login_required
def delete_jizda(jizda_id):
    jizda = Jizda.query.get_or_404(jizda_id)
    # Kontrola, zda jízda patří k vozidlu uživatele
    vozidlo = Vozidlo.query.get(jizda.vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění ke smazání této jízdy.', 'danger')
        return redirect(url_for('jizdy.index'))
    
    db.session.delete(jizda)
    db.session.commit()
    flash('Jízda byla úspěšně smazána!', 'success')
    return redirect(url_for('jizdy.index'))
