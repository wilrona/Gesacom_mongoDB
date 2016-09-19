__author__ = 'Ronald'


from flaskext import wtf
from flaskext.wtf import validators

class FormFonction(wtf.Form):
    libelle = wtf.StringField(label='Nom fonction', validators=[validators.Required(message='Champ obligatoire')])