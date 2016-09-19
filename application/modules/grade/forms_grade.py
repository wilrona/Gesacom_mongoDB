__author__ = 'Ronald'


from flaskext import wtf
from flaskext.wtf import validators

class FormGrade(wtf.Form):
    libelle = wtf.StringField(label='Nom du grade', validators=[validators.Required(message='Champ obligatoire')])