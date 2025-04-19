import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tvuj-tajny-klic-zde')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///kniha_jizd_v3.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PROTECTION = "strong"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    REMEMBER_COOKIE_DURATION = None
    SESSION_PERMANENT = False
    # Další konfigurace můžeš přidat sem
