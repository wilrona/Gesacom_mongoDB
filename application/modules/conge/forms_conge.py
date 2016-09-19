__author__ = 'Ronald'

from flaskext import wtf
from flaskext.wtf import validators
from ...modules import *
from models_conge import Ferier


def control_date(form, field):
    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')

    send_date = function.date_convert(field.data)

    if send_date.year != function.date_convert(dt).year:
        raise wtf.ValidationError('Cette date n\'est pas une date de l\'annee en cours')


def exist_date(form, field):
    date_field = datetime.datetime.combine(function.date_convert(field.data), datetime.datetime.min.time())
    exist_ferier = Ferier.objects(date=date_field)
    if len(exist_ferier):
        raise wtf.ValidationError('Cette date a deja ete cree')


class FormFerier(wtf.Form):
    id = wtf.HiddenField()
    date = wtf.DateField(label='Date du jour ferier :', format="%d/%m/%Y", validators=[validators.Required('Champ Obligatoire'), control_date, exist_date])
    description = wtf.TextAreaField(label='Description :', validators=[validators.Required('Champ Obligatoire')])