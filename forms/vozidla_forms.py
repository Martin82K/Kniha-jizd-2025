from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

class VozidloForm(FlaskForm):
    nazev = StringField('Název vozidla', validators=[DataRequired(), Length(min=2, max=100)])
    spz = StringField('SPZ', validators=[DataRequired(), Length(min=2, max=20)])
    palivo = StringField('Palivo', validators=[Length(max=50)])
    pocatecni_stav_km = IntegerField('Počáteční stav km', validators=[DataRequired()])
    poznamka = StringField('Poznámka')
    submit = SubmitField('Uložit vozidlo')
