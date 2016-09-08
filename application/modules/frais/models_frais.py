__author__ = 'Ronald'

from application import db
from ..projet.models_projet import Projet

class Frais(db.Document):
    libelle = db.StringField()
    factu = db.BooleanField()
    nfactu = db.BooleanField()



class FraisProjet(db.Document):
    montant = db.FloatField()
    facturable = db.BooleanField()
    projet_id = db.ReferenceField(Projet)
    frais_id = db.ReferenceField(Frais)