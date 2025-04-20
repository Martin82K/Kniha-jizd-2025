from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import db, Tankovani, Vozidlo
from forms.tankovani_forms import TankovaniForm

tankovani_bp = Blueprint('tankovani', __name__)

@tankovani_bp.route('/nove_tankovani', methods=['GET', 'POST'])
@login_required
def nove_tankovani():
    form = TankovaniForm()
    if form.validate_on_submit():
        aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
        if not aktivni_vozidlo_id:
            flash('Nejprve vyberte aktivní vozidlo', 'danger')
            return redirect(url_for('vozidla.vozidla'))
        vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
        tankovani = Tankovani(
            datum=form.datum.data,
            vozidlo_id=aktivni_vozidlo_id,
            stav_tachometru=form.stav_tachometru.data,
            litru=form.litru.data,
            cena_za_litr=form.cena_za_litr.data,
            celkova_cena=form.litru.data * form.cena_za_litr.data,
            poznamka=form.poznamka.data
        )
        db.session.add(tankovani)
        db.session.commit()
        flash('Tankování bylo uloženo.', 'success')
        return redirect(url_for('vozidla.vozidla'))
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    aktivni_vozidlo = None
    if aktivni_vozidlo_id:
        aktivni_vozidlo = Vozidlo.query.get(aktivni_vozidlo_id)
    return render_template('nove_tankovani.html', form=form, aktivni_vozidlo=aktivni_vozidlo)

@tankovani_bp.route('/prehled_tankovani')
@login_required
def prehled_tankovani():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    tankovani = Tankovani.query.order_by(Tankovani.datum.desc()).paginate(page=page, per_page=per_page)
    return render_template('prehled_tankovani.html', tankovani=tankovani)

@tankovani_bp.route('/edit_tankovani/<int:tankovani_id>', methods=['GET', 'POST'])
@login_required
def edit_tankovani(tankovani_id):
    tankovani = Tankovani.query.get_or_404(tankovani_id)
    form = TankovaniForm(obj=tankovani)
    if form.validate_on_submit():
        form.populate_obj(tankovani)
        tankovani.celkova_cena = form.litru.data * form.cena_za_litr.data
        db.session.commit()
        flash('Tankování bylo upraveno.', 'success')
        return redirect(url_for('tankovani.prehled_tankovani'))
    return render_template('edit_tankovani.html', form=form, tankovani=tankovani)
