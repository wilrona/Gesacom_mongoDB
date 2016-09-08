__author__ = 'Ronald'


from ...modules import *
import urlfetch

prefix = Blueprint('upload', __name__)


@prefix.route('/')
def index():
    url = "http://accentcom-time.com/api/roles"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..role.models_role import Roles

    role_admin = Roles.objects(valeur='super_admin').first()

    for data in result['data']:
        existe_role = Roles.objects(valeur=data['valeur']).first()
        if data['valeur'] != role_admin.valeur and not existe_role:
            role = Roles()
            role.titre = data['titre']
            role.valeur = data['valeur']
            role.description = data['description']
            role.action = data['action']
            role.active = data['active']
            role.save()

    # Enregistrement des references des parents au role concerne
    for data in result['data']:
        if data['parent']:
            current_role = Roles.objects(valeur=data['valeur']).first()
            parent_role = Roles.objects(valeur=data['parent']).first()
            current_role.parent = parent_role
            current_role.save()


    url = "http://accentcom-time.com/api/profil"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..profil.models_profil import Profil, ProfilRole
    for data in result['data']:
        existe_profil = Profil.objects(name=data['name']).first()
        if not existe_profil:
            profil = Profil()
            profil.name = data['name']
            profil.description = data['description']
            profil.active = data['active']
            profil_id = profil.save()

            for profil_role in data['roles']:
                pro_role = ProfilRole()
                pro_role.edit = profil_role['edit']
                pro_role.deleted = profil_role['delecte']

                role_profil = Roles.objects(valeur=profil_role['role']).first()
                pro_role.role_id = role_profil
                pro_role.profil_id = profil_id
                pro_role.save()



    url = "http://accentcom-time.com/api/societe"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..societe.models_societe import Societe
    for data in result['data']:
        existe_societe = Societe.objects.first()
        if not existe_societe:
            societe = Societe()
            societe.name = data['name']
            societe.adress = data['adress']
            societe.bp = data['bp']
            societe.capital = data['capital']
            societe.email = data['email']
            societe.numcontr = data['numcontr']
            societe.pays = data['pays']
            societe.phone = data['phone']
            societe.registcom = data['registcom']
            societe.siteweb = data['siteweb']
            societe.slogan = data['slogan']
            societe.typEnt = data['typEnt']
            societe.ville = data['ville']
            societe.save()


    url = "http://accentcom-time.com/api/site"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..site.models_site import Site
    existe_societe = Societe.objects.first()
    for data in result['data']:
        exist_data = Site.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            site = Site()
            site.libelle = data['libelle']
            site.societe = existe_societe
            site.save()



    url = "http://accentcom-time.com/api/departement"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..departement.models_dep import Departement
    for data in result['data']:
        exist_data = Departement.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            dep = Departement()
            dep.libelle = data['libelle']
            dep.societe = existe_societe
            dep.save()



    url = "http://accentcom-time.com/api/fonction"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..fonction.models_fct import Fonction
    for data in result['data']:
        exist_data = Fonction.objects(libelle=data['libelle']).first()
        if not exist_data:
            fonction = Fonction()
            fonction.libelle = data['libelle']
            fonction.save()



    url = "http://accentcom-time.com/api/grade"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..grade.models_grade import Grade
    for data in result['data']:
        exist_data = Grade.objects(libelle=data['libelle']).first()
        if not exist_data:
            grade = Grade()
            grade.libelle = data['libelle']
            grade.save()



    url = "http://accentcom-time.com/api/prestation"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..prestation.models_prest import Prestation
    for data in result['data']:
        exist_data = Prestation.objects(sigle=data['sigle']).first()
        if not exist_data:
            prest = Prestation()
            prest.libelle = data['libelle']
            prest.factu = data['factu']
            prest.nfactu = data['nfactu']
            prest.sigle = data['sigle']
            prest.save()


    url = "http://accentcom-time.com/api/frais"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..frais.models_frais import Frais
    for data in result['data']:
        exist_data = Frais.objects(libelle=data['libelle']).first()
        if not exist_data:
            frais = Frais()
            frais.libelle = data['libelle']
            frais.factu = data['factu']
            frais.nfactu = data['nfactu']
            frais.save()




    url = "http://accentcom-time.com/api/charge"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..charge.models_charge import Charge
    from ..budget.models_budget import ChargeBudget
    for data in result['data']:
        exist_data = Charge.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            charge = Charge()
            charge.libelle = data['libelle']
            charge.societe = existe_societe
            charge_id = charge.save()

            for budget in data['budget']:
                bud = ChargeBudget()
                bud.date_app = function.datetime_convert(budget['date_app'])
                bud.montant = budget['montant']
                bud.charge_id = charge_id
                bud.save()



    url = "http://accentcom-time.com/api/client"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..client.models_client import Client, Contact
    from ..budget.models_budget import ClientBudget
    for data in result['data']:
        exist_data = Client.objects(ref=data['ref']).first()
        if not exist_data:
            client = Client()
            client.name = data['name']
            client.ref = data['ref']
            client.ville = data['ville']
            client.adresse = data['adresse']
            client.bp = data['bp']
            client.date_created = function.datetime_convert(data['date_created'])
            client.email = data['email']
            client.myself = data['myself']
            client.pays = data['pays']
            client.phone = data['phone']
            client.prospect = data['prospect']
            client_id = client.save()

            for contact in data['contacts']:
                cont = Contact()
                cont.first_name = contact['first_name']
                cont.last_name = contact['last_name']
                cont.email = contact['email']
                cont.phone1 = contact['phone1']
                cont.phone2 = contact['phone2']
                cont.client_id = client_id
                cont.save()

            for budget in data['budgets']:
                bud = ClientBudget()
                bud.date_app = function.datetime_convert(budget['date_app'])
                bud.montant = budget['montant']
                bud.client_id = client_id
                bud.save()


    url = "http://accentcom-time.com/api/client"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..domaine.models_domaine import Domaine, Service
    for data in result['data']:
        exist_data = Domaine.objects(code=data['code']).first()
        if exist_data:
            domaine = Domaine()
            domaine.code = data['code']
            domaine.libelle = data['libelle']
            domaine_id = domaine.save()

            for service in data['services']:
                serv = Service()
                serv.code = service['code']
                serv.libelle = service['libelle']
                serv.domaine = domaine_id
                serv.save()




    url = "http://accentcom-time.com/api/user"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..user.models_user import Users, UserRole, Horaire
    for data in result['data']:
        exist_data = Users.objects(email=data['email']).first()
        if not exist_data:
            user = Users()
            user.email = data['email']
            user.date_create = function.datetime_convert(data['date_create'])
            user.matricule = data['matricule']
            user.is_enabled = data['is_enabled']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.logged = data['logged']
            user.date_last_logged = data['date_last_logged']
            user.google_id = data['google_id']
            user.date_update = function.datetime_convert(data['date_update'])
            user.tauxH = data['tauxH']
            user.date_start = function.datetime_convert(data['date_start'])

            if data['fonction_id']:
                fonction = Fonction.objects(libelle=data['fonction_id']).first()
                user.fonction_id = fonction

            if data['departement_id']:
                departement = Departement.objects(libelle=data['departement_id']).first()
                user.departement_id = departement

            if data['grade_id']:
                grade = Grade.objects(libelle=data['grade_id']).first()
                user.grade_id = grade

            if data['site_id']:
                site = Site.objects(libelle=data['site_id']).first()
                user.site_id = site

            user_id = user.save()

            for role in data['roles']:
                userR = UserRole()
                userR.deleted = role['delete']
                userR.edit = role['edit']

                rol_id = Roles.objects(valeur=role['role']).first()
                userR.role_id = rol_id

                userR.user_id = user_id
                userR.save()

            for horaire in data['horaires']:
                horai = Horaire()
                horai.date_start = function.datetime_convert(horaire['date_start'])

                horai.montant = horaire['montant']
                horai.user = user_id
                horai.save()



        url = "http://accentcom-time.com/api/budget"
        result = urlfetch.get(url)
        result = result.content
        result = json.loads(result)








    if result['status'] == 200:
        return 'True'
    else:
        return 'False'