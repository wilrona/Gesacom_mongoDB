__author__ = 'Ronald'


from flaskext import wtf
from flaskext.wtf import validators

class FormDep(wtf.Form):
    libelle = wtf.StringField(label='Nom du depart.', validators=[validators.Required(message='Champ obligatoire')])