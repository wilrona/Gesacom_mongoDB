__author__ = 'Ronald'


from application import db
from ..user.models_user import Users
from ..tache.models_tache import Tache
from ..frais.models_frais import FraisProjet


class Temps(db.Document):
    date_start = db.DateTimeField()
    date_end = db.DateTimeField()
    user_id = db.ReferenceField(Users)
    tache_id = db.ReferenceField(Tache)


class DetailTemps(db.Document):
    date = db.DateTimeField()
    description = db.StringField()
    heure = db.DateTimeField()
    jour = db.IntField()
    conversion = db.FloatField()
    temps_id = db.ReferenceField(Temps)
    ordre = db.IntField()
    parent = db.IntField()


class DetailFrais(db.Document):
    date = db.DateTimeField()
    description = db.StringField()
    montant = db.FloatField()
    detail_fdt = db.ReferenceField(DetailTemps)
    temps_id = db.ReferenceField(Temps)
    frais_projet_id = db.ReferenceField(FraisProjet)
