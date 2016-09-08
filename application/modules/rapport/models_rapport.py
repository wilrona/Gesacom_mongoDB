__author__ = 'Ronald'


from application import db


class fdt_coll(db.Document):
    absence = db.FloatField()
    conge = db.FloatField()
    ferier = db.FloatField()
    administration = db.FloatField()
    formation = db.FloatField()
    developpement = db.FloatField()
    prod_fact = db.FloatField()
    prod_nfact = db.FloatField()
    heure_nchargee = db.FloatField()


