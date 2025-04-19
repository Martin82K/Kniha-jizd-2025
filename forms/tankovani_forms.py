from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length

class TankovaniForm(FlaskForm):
    datum = DateTimeField('Datum a čas', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    stav_tachometru = IntegerField('Stav tachometru', validators=[DataRequired()])
    litru = FloatField('Litry', validators=[DataRequired()])
    cena_za_litr = FloatField('Cena za litr', validators=[DataRequired()])
    celkova_cena = FloatField('Celková cena', validators=[DataRequired()])
    poznamka = StringField('Poznámka', validators=[Length(max=255)])
    submit = SubmitField('Uložit tankování')
