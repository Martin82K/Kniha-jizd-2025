from flask import Blueprint, render_template
from flask_login import login_required
from models import Jizda

statistiky_bp = Blueprint('statistiky', __name__)

@statistiky_bp.route('/statistiky')
@login_required
def statistiky():
    # Zde bude logika pro výpočet statistik
    return render_template('statistiky.html')
