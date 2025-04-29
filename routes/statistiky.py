from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Jizda, Vozidlo, Tankovani

statistiky_bp = Blueprint('statistiky', __name__)

@statistiky_bp.route('/statistiky')
@login_required
def statistiky():
    vozidla = Vozidlo.query.filter_by(user_id=current_user.id).all()
    statistiky = []
    for vozidlo in vozidla:
        jizdy = Jizda.query.filter_by(vozidlo_id=vozidlo.id).all()
        celkem_km_soukroma = sum(j.pocet_km for j in jizdy if (j.typ_jizdy or '').lower() in ['soukromá', 'soukroma'])
        celkem_km_pracovni = sum(j.pocet_km for j in jizdy if (j.typ_jizdy or '').lower() in ['pracovní', 'pracovni', 'služební', 'sluzebni'])
        celkem_phm = sum(t.celkova_cena for t in vozidlo.tankovani)
        celkem_km = celkem_km_soukroma + celkem_km_pracovni
        # Průměrná spotřeba (l/100km)
        celkem_litru = sum(t.litru for t in vozidlo.tankovani)
        prumerna_spotreba = round((celkem_litru / celkem_km * 100), 2) if celkem_km > 0 else None
        naklady_na_km = round(celkem_phm / celkem_km, 2) if celkem_km > 0 else 0
        statistiky.append({
            'vozidlo': vozidlo.nazev,
            'spz': vozidlo.spz,
            'celkem_km_soukroma': celkem_km_soukroma,
            'celkem_km_pracovni': celkem_km_pracovni,
            'celkem_phm': celkem_phm,
            'prumerna_spotreba': prumerna_spotreba,
            'naklady_na_km': naklady_na_km
        })
    return render_template('statistiky.html', statistiky=statistiky)
