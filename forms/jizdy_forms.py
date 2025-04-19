from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length

class JizdaForm(FlaskForm):
    datum = DateTimeField('Datum a čas', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    misto_odjezdu = StringField('Odkud', validators=[DataRequired(), Length(min=2, max=200)])
    misto_prijezdu = StringField('Kam', validators=[DataRequired(), Length(min=2, max=200)])
    pocet_km = FloatField('Počet km', validators=[DataRequired()])
    ucel_jizdy = StringField('Účel jízdy', validators=[DataRequired(), Length(min=2, max=200)])
    stav_tachometru = IntegerField('Stav tachometru', validators=[DataRequired()])
    typ_jizdy = SelectField('Typ jízdy', choices=[('služební','Služební'),('soukromá','Soukromá')], validators=[DataRequired()])
    submit = SubmitField('Uložit jízdu')
