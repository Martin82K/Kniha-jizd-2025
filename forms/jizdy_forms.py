from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Optional

class JizdaForm(FlaskForm):
    datum = DateField('Datum', format='%Y-%m-%d', validators=[DataRequired()])
    misto_odjezdu = StringField('Odkud', validators=[DataRequired()])
    misto_prijezdu = StringField('Kam', validators=[DataRequired()])
    pocet_km = FloatField('Počet km', validators=[DataRequired()])
    ucel_jizdy = StringField('Účel jízdy', validators=[DataRequired()])
    stav_tachometru = IntegerField('Stav tachometru', validators=[Optional()])  # Přidáno zpět
    typ_jizdy = SelectField('Typ jízdy', choices=[('Služební', 'Služební'), ('Soukromá', 'Soukromá')], validators=[DataRequired()])
    ridic = StringField('Řidič', validators=[DataRequired()])
    submit = SubmitField('Uložit jízdu')
