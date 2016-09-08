__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from .models_prest import Prestation

def verif_facturable(form, field):
    if not form.factu.data and not form.nfactu.data:
        raise wtf.ValidationError('Une prestation doit etre soit facturable ou non facturable ou les deux.')


def verif_sigle(form, field):
    pret_exist = Prestation.objects(
        sigle=field.data
    )
    if len(pret_exist) == 1:
        current = pret_exist.first()
        if current.id != form.id.data:
            raise wtf.ValidationError('Il existe une prestation avec le meme sigle.')


class FormPrestation(wtf.Form):
    libelle = wtf.StringField(label='Nom prestation', validators=[validators.Required(message='Champ obligatoire')])
    factu = wtf.BooleanField(label='Facturable ?', validators=[verif_facturable])
    nfactu = wtf.BooleanField(label='Non Facturable ?')
    sigle = wtf.SelectField(label='Selectionez un sigle', choices=[('', ''), ('ADM', 'Administration'), ('FOR', 'Formation'), ('DEV', 'Developpement'), ('PRO', 'Production'), ('CONG', 'Conge'), ('ABS', 'Absence'), ('FER', 'Ferier')], coerce=str, validators=[verif_sigle])
    id = wtf.HiddenField()