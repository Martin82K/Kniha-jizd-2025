from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import db, Jizda, Vozidlo
from forms.jizdy_forms import JizdaForm

jizdy_bp = Blueprint('jizdy', __name__)

@jizdy_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    jizdy = Jizda.query.order_by(Jizda.datum.desc()).paginate(page=page, per_page=per_page)
    return render_template('index.html', jizdy=jizdy)

@jizdy_bp.route('/nova_jizda', methods=['GET', 'POST'])
@login_required
def nova_jizda():
    form = JizdaForm()
    if form.validate_on_submit():
        aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
        if not aktivni_vozidlo_id:
            flash('Nejprve vyberte aktivní vozidlo', 'danger')
            return redirect(url_for('vozidla.vozidla'))
        vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
        jizda = Jizda(
            datum=form.datum.data,
            vozidlo_id=aktivni_vozidlo_id,
            ridic=current_user.prijmeni,
            misto_odjezdu=form.misto_odjezdu.data,
            misto_prijezdu=form.misto_prijezdu.data,
            pocet_km=form.pocet_km.data,
            ucel_jizdy=form.ucel_jizdy.data,
            stav_tachometru=form.stav_tachometru.data,
            typ_jizdy=form.typ_jizdy.data
        )
        db.session.add(jizda)
        db.session.commit()
        flash('Jízda byla uložena.', 'success')
        return redirect(url_for('jizdy.index'))
    return render_template('nova_jizda.html', form=form)

@jizdy_bp.route('/edit_jizda/<int:jizda_id>', methods=['GET', 'POST'])
@login_required
def edit_jizda(jizda_id):
    jizda = Jizda.query.get_or_404(jizda_id)
    form = JizdaForm(obj=jizda)
    if form.validate_on_submit():
        form.populate_obj(jizda)
        db.session.commit()
        flash('Jízda byla upravena.', 'success')
        return redirect(url_for('jizdy.index'))
    return render_template('edit_jizda.html', form=form, jizda=jizda)
