__author__ = 'wilrona'

from ...modules import *
from ..role.models_role import Roles
from ..site.models_site import Site
from ..departement.models_dep import Departement
from ..fonction.models_fct import Fonction
from ..grade.models_grade import Grade


class Users(db.Document):

    email = db.StringField()
    date_create = db.DateTimeField()
    matricule = db.StringField()

    is_enabled = db.BooleanField()
    first_name = db.StringField()
    last_name = db.StringField()
    logged = db.BooleanField()
    date_last_logged = db.DateTimeField()
    google_id = db.StringField()
    date_update = db.DateTimeField()

    fonction_id = db.ReferenceField(Fonction)
    site_id = db.ReferenceField(Site)
    departement_id = db.ReferenceField(Departement)
    grade_id = db.ReferenceField(Grade)

    tauxH = db.FloatField()
    date_start = db.DateTimeField()

    def is_active(self):
        return self.is_enabled

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = ''+str(self.last_name)+' '+str(self.first_name)+''
        return full_name

    def has_roles(self, requirements, accesibles=None):

        user_role = UserRole.objects(
            user_id= self.id
        )

        user_roles = [role.get_role().valeur for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True

                        if accesibles and role_name != 'super_admin':
                            role = Roles.objects(valeur=role_name).first()

                            role_user = UserRole.query(Q(user_id=self.id) & Q(role_id=role.id)).first()

                            for accesible in accesibles:
                                if accesible == 'edit' and not role_user.edit:
                                    authorized = False
                                    break
                                if accesible == 'delete' and not role_user.delete:
                                    authorized = False
                                    break
                        else:
                            break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
                else:
                    return True
            else:
                # this is a role_name requirement
                role_name = requirement

                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False
                else:
                    if accesibles and role_name != 'super_admin':

                        role = Roles.objects(valeur=role_name).first()

                        role_user = UserRole.objects(
                            Q(user_id=self.id) & Q(role_id=role.id)
                        ).first()

                        for accesible in accesibles:
                            if accesible == 'edit' and not role_user.edit:
                                return False
                            if accesible == 'delete' and not role_user.delete:
                                return False

        # All requirements have been met: return True
        return True

    def time_user(self, date_start=None, date_end=None):
        from ..temps.models_temps import DetailTemps, Temps

        the_time_user = []

        temps = Temps.objects(user_id=self.id)

        for temp in temps:
            if date_start and date_end:
                details = DetailTemps.objects(
                    Q(date__gte=date_start) &
                    Q(date__lte=date_end) &
                    Q(temps_id=temp.id)
                )
            else:

                details = DetailTemps.objects(
                    temps_id = temp.id
                )
            for detail in details:
                the_time_user.append(detail)

        return the_time_user

    def projet_user(self):
        from ..tache.models_tache import Tache

        List_projet = []

        for tache in Tache.objects(user_id=self.id):
            if tache.projet_id and tache.get_projet().facturable and tache.get_projet().id not in List_projet:
                List_projet.append(tache.get_projet().id)

        return List_projet

    def valeur_facture(self):
        montant = 0.0
        for projet_id in self.projet_user():
            ratio = projet_id.ratio_user(self.id)

            montant_sur_projet = projet_id.montant * ratio

            montant += montant_sur_projet

        return montant


class UserRole(db.Document):
    role_id = db.ReferenceField(Roles)
    user_id = db.ReferenceField(Users)
    edit = db.BooleanField(default=False)
    deleted = db.BooleanField(default=False)

    def get_role(self):
        return Roles.objects.get(id=self.role_id.id)

    def get_user(self):
        return Users.objects.get(id=self.user_id.id)

class Horaire(db.Document):
    date_start = db.DateTimeField()
    montant = db.FloatField()
    user = db.ReferenceField(Users)






