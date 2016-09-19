__author__ = 'Ronald'


from flaskext import wtf
from flaskext.wtf import validators

class FormSite(wtf.Form):
    libelle = wtf.StringField(label='Nom du site', validators=[validators.Required(message='Champ obligatoire')])