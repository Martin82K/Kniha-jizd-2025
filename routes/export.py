from flask import Blueprint, send_file, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Vozidlo, Jizda
import calendar
from datetime import datetime
import os
import pandas as pd

export_bp = Blueprint('export', __name__)

@export_bp.route('/export_xls/<int:rok>/<int:mesic>')
@login_required
def export_xls(rok, mesic):
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'danger')
        return redirect(url_for('vozidla.vozidla'))
    vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění k tomuto vozidlu', 'danger')
        return redirect(url_for('jizdy.index'))
    _, posledni_den = calendar.monthrange(rok, mesic)
    zacatek_mesice = datetime(rok, mesic, 1)
    konec_mesice = datetime(rok, mesic, posledni_den, 23, 59, 59)
    jizdy = Jizda.query.filter(
        Jizda.vozidlo_id == aktivni_vozidlo_id,
        Jizda.datum >= zacatek_mesice,
        Jizda.datum <= konec_mesice
    ).order_by(Jizda.datum).all()
    # ...zbytek logiky exportu do XLSX...
    # (zkráceno pro příklad)
    return 'Export XLS hotov!'

@export_bp.route('/export_pdf/<int:rok>/<int:mesic>')
@login_required
def export_pdf(rok, mesic):
    aktivni_vozidlo_id = session.get('aktivni_vozidlo_id')
    if not aktivni_vozidlo_id:
        flash('Nejprve vyberte aktivní vozidlo', 'danger')
        return redirect(url_for('vozidla.vozidla'))
    vozidlo = Vozidlo.query.get_or_404(aktivni_vozidlo_id)
    if vozidlo.user_id != current_user.id:
        flash('Nemáte oprávnění k tomuto vozidlu', 'danger')
        return redirect(url_for('jizdy.index'))
    _, posledni_den = calendar.monthrange(rok, mesic)
    zacatek_mesice = datetime(rok, mesic, 1)
    konec_mesice = datetime(rok, mesic, posledni_den, 23, 59, 59)
    jizdy = Jizda.query.filter(
        Jizda.vozidlo_id == aktivni_vozidlo_id,
        Jizda.datum >= zacatek_mesice,
        Jizda.datum <= konec_mesice
    ).order_by(Jizda.datum).all()
    # ...zbytek logiky exportu do PDF...
    # (zkráceno pro příklad)
    return 'Export PDF hotov!'
