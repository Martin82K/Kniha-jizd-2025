from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import db, Vozidlo
from forms.vozidla_forms import VozidloForm

vozidla_bp = Blueprint('vozidla', __name__)

@vozidla_bp.route('/vozidla')
@login_required
def vozidla():
    vozidla = Vozidlo.query.filter_by(user_id=current_user.id).all()
    return render_template('vozidla.html', vozidla=vozidla)

@vozidla_bp.route('/pridat_vozidlo', methods=['GET', 'POST'])
@login_required
def pridat_vozidlo():
    form = VozidloForm()
    if form.validate_on_submit():
        vozidlo = Vozidlo(
            nazev=form.nazev.data,
            spz=form.spz.data,
            pocatecni_stav_km=form.pocatecni_stav_km.data,
            aktualni_stav_km=form.pocatecni_stav_km.data,
            user_id=current_user.id
        )
        db.session.add(vozidlo)
        db.session.commit()
        flash('Vozidlo bylo přidáno.', 'success')
        return redirect(url_for('vozidla.vozidla'))
    return render_template('pridat_vozidlo.html', form=form)

@vozidla_bp.route('/edit_vozidlo/<int:vozidlo_id>', methods=['GET', 'POST'])
@login_required
def edit_vozidlo(vozidlo_id):
    vozidlo = Vozidlo.query.get_or_404(vozidlo_id)
    form = VozidloForm(obj=vozidlo)
    if form.validate_on_submit():
        form.populate_obj(vozidlo)
        db.session.commit()
        flash('Vozidlo bylo upraveno.', 'success')
        return redirect(url_for('vozidla.vozidla'))
    return render_template('edit_vozidlo.html', form=form, vozidlo=vozidlo)
