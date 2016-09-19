__author__ = 'Ronald'

from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput
from ...modules import *
from models_projet import Projet, BesoinFinancier


def controle_date_end(form, field):
    date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
    date_end = datetime.datetime.combine(function.date_convert(field.data), datetime.datetime.min.time())
    if date_end < date_start:
        raise wtf.ValidationError('La date de fin doit etre > la date de debut')


def controle_date_start(form, field):
    date_start = datetime.datetime.combine(function.date_convert(field.data), datetime.datetime.min.time())
    # if datetime.date.today() > date_start and not form.id.data:
    #     raise wtf.ValidationError('La date de debut doit etre >= date en cours')

    if form.id.data:
        projet = Projet.objects.get(id=form.id.data)
        if projet.date_start > date_start:
            raise wtf.ValidationError('La nouvelle date de debut doit etre >= a la date modifie')


def controle_date(form, field):
    date_echeance = function.date_convert(field.data)

    if form.id.data:
        if form.relance.data or form.solde.data:
            if date_echeance < datetime.date.today():
                raise wtf.ValidationError('La date de la relance doit etre superieur ou egale a la date en cours')


def controle_avance(form, field):
    if form.id.data and form.solde.data:
        besoin = BesoinFinancier.objects.get(id=form.id.data)
        solde = besoin.montant - besoin.paye
        if float(field.data) > solde:
            raise wtf.ValidationError('Le montant de l\'avance est superieur au solde')


class FormProjet(wtf.Form):
    titre = wtf.StringField(label='Nom du projet', validators=[validators.Required('Champ Obligatoire')])
    heure = wtf.IntegerField(label='Nombre d\'heure', default=0, widget=NumberInput(),validators=[validators.Required('Champ Obligatoire')])
    montant = wtf.FloatField(label='Montant vendu', validators=[validators.Required('Champ Obligatoire')])
    date_start = wtf.DateField(label='Date de debut', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), controle_date_start])
    date_end = wtf.DateField(label='Date de fin', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), controle_date_end])
    facturable = wtf.BooleanField(label='Facturable ?')
    domaine_id = wtf.SelectField(label='Domaine ', coerce=str, validators=[validators.Required('Champ Obligatoire')])
    client_id = wtf.SelectField(label='Client', coerce=str, validators=[validators.Required('Champ Obligatoire')])
    service_id = wtf.StringField(label='Ligne de service', validators=[validators.Required('Champ Obligatoire')])
    prospect_id = wtf.StringField(label='Pour le compte de')
    responsable_id = wtf.SelectField(label='Responsable', coerce=str, validators=[validators.Required('Champ Obligatoire')])
    closed = wtf.BooleanField(label='Cloturer ?')
    id = wtf.HiddenField()


class FormBesoin(wtf.Form):
    commande = wtf.StringField(label="Commande", validators=[validators.Required('Champ Obligatoires')])
    date_echeance = wtf.DateField(label='Date echeance', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), controle_date])
    montant = wtf.FloatField(label='Montant', default=0, widget=NumberInput(), validators=[validators.Required('Champ Obligatoire')])
    avance = wtf.FloatField(label='Avance', default=0, widget=NumberInput(), validators=[controle_avance])
    projet_id = wtf.SelectField(label='Projet', coerce=str, validators=[validators.Required('Champ Obligatoire')])
    fournisseur = wtf.StringField(label='Fournisseur', validators=[validators.Required('Champ Obligatoire')])
    solde = wtf.HiddenField()
    relance = wtf.HiddenField()
    id = wtf.HiddenField()
