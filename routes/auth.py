from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
from forms.auth_forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_account_valid():
                flash('Uživateli vypršel přístup', 'danger')
                return redirect(url_for('auth.login'))
            session.permanent = False
            login_user(user)
            next_page = request.args.get('next')
            flash('Přihlášení bylo úspěšné!', 'success')
            return redirect(next_page or url_for('index'))
        flash('Nesprávné přihlašovací údaje', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Byl jste úspěšně odhlášen.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        prijmeni = form.prijmeni.data
        username = prijmeni.lower()
        email = form.email.data
        if User.query.filter_by(username=username).first():
            flash('Toto uživatelské jméno již existuje', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Tento email již existuje', 'danger')
            return redirect(url_for('auth.register'))
        new_user = User(username=username, prijmeni=prijmeni, email=email)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrace byla úspěšná. Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)
