__author__ = 'wilrona'

from ...modules import *
from application import google_login
from models_user import Users, UserRole, Fonction, Site, Departement, Grade, Horaire, Roles
from ..profil.models_profil import Profil, ProfilRole
from forms_user import FormUser, FormHoraire

prefix = Blueprint('user', __name__)
prefix_param = Blueprint('user_param', __name__)


@google_login.user_loader
def load_user(userid):
    return Users.objects(id=userid).first()


@prefix.route('/oauth2callback')
@google_login.oauth2callback
def login(token, userinfo, **params):

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    param = params.get('extra')
    if param:
        if userinfo['hd'] and (userinfo['hd'] == 'accentcom-cm.com' or userinfo['hd'] == 'accentcom.agency'):
            if param == 'superadmin':
                admin_role = Roles.objects(valeur='super_admin')

                if admin_role:
                    flash('il existe deja un super administrateur', 'warning')
                    return redirect(url_for('home.index'))
                else:
                    Role = Roles()
                    Role.valeur = 'super_admin'
                    role_id = Role.save()

                    User = Users()
                    User.first_name = userinfo['family_name']
                    User.last_name = userinfo['given_name']
                    User.email = userinfo['email']
                    User.google_id = userinfo['id']
                    User.is_enabled = True
                    User.date_create = function.datetime_convert(date_auto_nows)
                    User.date_update = function.datetime_convert(date_auto_nows)
                    user_id = User.save()

                    User_Role = UserRole()
                    User_Role.role_id = role_id
                    User_Role.user_id = user_id
                    User_Role.save()

                    flash('Creation du compte admin avec success. Vous pouvez vous connecter', 'success')
                    return redirect(url_for('home.index'))
            elif param == 'utilisateur':
                User_exist = Users.objects(google_id=userinfo['id']).first()

                if User_exist:
                    if User_exist.is_enabled:
                        session['user_id'] = str(User_exist.id)
                        User_exist.logged = True
                        User_exist.date_last_logged = function.datetime_convert(date_auto_nows)
                        User_exist.date_update = function.datetime_convert(date_auto_nows)
                        User_exist.save()
                        return redirect(url_for('tache.me'))
                    else:
                        flash("Votre Compte est en attente d'activation de vos parametres. Contactez l'administrateur", 'warning')
                        return redirect(url_for('home.index'))
                else:
                    User = Users()
                    User.first_name = userinfo['family_name']
                    User.last_name = userinfo['given_name']
                    User.email = userinfo['email']
                    User.google_id = userinfo['id']
                    User.date_create = function.datetime_convert(date_auto_nows)
                    User.date_update = function.datetime_convert(date_auto_nows)
                    user_id = User.save()

                    flash(""+userinfo['name']+" Votre Compte est en attente d'activation de vos parametres. Contactez l'administrateur", 'warning')
                    return redirect(url_for('home.index'))
        else:
            flash('Connectez vous avec une adresse mail du Domaine "accentcom-cm.com"', 'danger')
            return redirect(url_for('home.index'))
    else:
        flash('Vous ne pouvez pas acceder dans cette url', 'danger')
        return redirect(url_for('home.index'))


@prefix.route('/logout')
def logout():
    change = None

    if 'user_id' in session:
        UserLogout = Users.objects.get(id=session.get('user_id'))
        UserLogout.logged = False
        change = UserLogout.save()

    if change:
        session.pop('user_id')

    return redirect(url_for('home.index'))


@prefix_param.route('/')
@login_required
@roles_required([('super_admin', 'user')])
def index():
    menu = 'user'
    submenu = 'users'
    title_page = 'Parametre - Utilisateurs'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    limit = 10
    offset = ((page - 1) * 10)

    count = Users.objects(email__ne='admin@accentcom-cm.com').count()
    users = Users.objects(email__ne='admin@accentcom-cm.com').skip(offset).limit(limit)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='users')

    return render_template('user/index.html', **locals())


@prefix_param.route('/infos/<objectid:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'user_infos')])
def infos(user_id):
    menu = 'user'
    submenu = 'users'
    context = 'information'
    title_page = 'Parametre - Utilisateurs'

    user = Users.objects.get(id=user_id)
    form = FormUser(obj=user)

    if user.fonction_id:
        form.fonction_id.data = str(user.fonction_id.id)
    form.fonction_id.choices = [(0, 'Selectionnez une fonction')]
    for choice in Fonction.objects():
        form.fonction_id.choices.append((str(choice.id), choice.libelle))

    if user.site_id:
        form.site_id.data = str(user.site_id.id)
    form.site_id.choices = [(0, 'Selectionnez un site')]
    for choice in Site.objects():
        form.site_id.choices.append((str(choice.id), choice.libelle))

    if user.grade_id:
        form.grade_id.data = str(user.grade_id.id)
    form.grade_id.choices = [(0, 'Selectionnez un grade')]
    for choice in Grade.objects():
        form.grade_id.choices.append((str(choice.id), choice.libelle))

    if user.departement_id:
        form.departement_id.data = str(user.departement_id.id)
    form.departement_id.choices = [(0, 'Selectionnez un departement')]
    for choice in Departement.objects():
        form.departement_id.choices.append((str(choice.id), choice.libelle))

    if form.validate_on_submit() and request.method == 'POST' and current_user.has_roles([('super_admin', 'user_infos')], ['edit']):

        fonction = Fonction.objects.get(id=form.fonction_id.data)
        user.fonction_id = fonction

        site = Site.objects.get(id=form.site_id.data)
        user.site_id = site

        grade = Grade.objects.get(id=form.grade_id.data)
        user.grade_id = grade

        departement = Departement.objects.get(id=form.departement_id.data)
        user.departement_id = departement

        user.matricule = form.matricule.data
        user.categorie = form.categorie.data

        user.is_enabled = True

        if form.date_start.data:
            user.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())

        user.save()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('user_param.infos', user_id=user_id))

    return render_template('user/infos.html', **locals())


@prefix_param.route('/permission/<objectid:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'user_permission')])
def permission(user_id):
    menu = 'user'
    submenu = 'users'
    context = 'permission'
    title_page = 'Parametre - Utilisateurs'

    user = Users.objects.get(id=user_id)

    # liste des roles lie a l'utiliasteur en cours
    attrib = UserRole.objects(
        user_id = user.id
    )
    attrib_list = [role.role_id.id for role in attrib]

    # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
    edit = UserRole.objects(Q(user_id=user.id) & Q(edit=True))
    edit_list = [role.role_id.id for role in edit]

    # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
    delete = UserRole.objects(Q(user_id=user.id) & Q(deleted=True))
    delete_list = [role.role_id.id for role in delete]


    liste_role = []
    data_role = Roles.objects(
        valeur__ne='super_admin'
    )

    for role in data_role:
        if not role.parent:
            module = {}
            module['titre'] = role.titre
            module['id'] = role.id
            enfants = Roles.objects(
                parent = role.id
            )
            module['role'] = []
            for enfant in enfants:
                rol = {}
                rol['id'] = enfant.id
                rol['titre'] = enfant.titre
                rol['action'] = enfant.action
                module['role'].append(rol)
            liste_role.append(module)

    # liste des profils de l'application
    list_profil = Profil.objects(
        active=True
    )

    profil_select = None
    if request.args.get('profil') and request.method == 'GET':

        profil_select = int(request.args.get('profil'))
        profil_request = Profil.objects.get(id=request.args.get('profil'))

        attrib = ProfilRole.objects(
            profil_id= profil_request.id
        )

        attrib_list = [role.role_id.id for role in attrib]

        # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
        edit = ProfilRole.objects(Q(profil_id=profil_request) & Q(edit=True))
        edit_list = [role.role_id.id for role in edit]

        # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
        delete = ProfilRole.objects(Q(profil_id=profil_request.id) & Q(deleted=True))
        delete_list = [role.role_id.id for role in delete]


    if request.method == 'POST' and current_user.has_roles([('super_admin', 'user_permission')], ['edit']):

        form_attrib = request.form.getlist('attrib')

        # if not form_attrib and attrib_list:
        #     flash('Les utilisateurs ne doivent pas exister sans permission dans l\'application', 'warning')
        #     return redirect(url_for('user_param.permission', user_id=user_id))
        # elif form_attrib:
        #     user.is_enabled = True
        #     user.put()

        form_edit = request.form.getlist('edit')
        form_delete = request.form.getlist('delete')

        # liste des roles lie au profil et supprimer ce qui ne sont plus attribue
        current_profil_role = UserRole.objects(
            user_id = user.id
        )
        for current in current_profil_role:
            if current.role_id.id not in form_attrib:
                current.delete()

        # Insertion des roles et authorisation en provenance du formulaire
        for attrib in form_attrib:

            role_form = Roles.objects.get(id=attrib)

            profil_role_exist = UserRole.objects(Q(role_id=role_form.id) & Q(user_id=user.id)).first()

            if profil_role_exist:
                if attrib in form_edit:
                    profil_role_exist.edit = True
                else:
                    profil_role_exist.edit = False

                if attrib in form_delete:
                    profil_role_exist.deleted = True
                else:
                    profil_role_exist.deleted = False

                profil_role_exist.save()
            else:
                profil_role_create = UserRole()
                profil_role_create.role_id = role_form
                profil_role_create.user_id = user
                if attrib in form_edit:
                    profil_role_create.edit = True
                else:
                    profil_role_create.edit = False

                if attrib in form_delete:
                    profil_role_create.deleted = True
                else:
                    profil_role_create.deleted = False

                profil_role_create.save()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('user_param.permission', user_id=user_id))

    return render_template('user/permission.html', **locals())

###### TRAITEMENT DES TAUX HORAIRES #########
@prefix_param.route('/horaire/<objectid:user_id>')
@login_required
@roles_required([('super_admin', 'user_horaire')])
def horaire(user_id):
    menu = 'user'
    submenu = 'users'
    context = 'horaire'
    title_page = 'Parametre - Utilisateurs'

    user = Users.objects.get(id=user_id)

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)
    date_auto_nows = function.datetime_convert(date_auto_nows)

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    offset = 0
    limit = 10
    if page > 1:
        offset = ((page - 1) * 10)

    count = Horaire.objects(user=user.id).order_by('-date_start').count()
    datas = Horaire.objects(user=user.id).order_by('-date_start').skip(offset).limit(limit)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='horaires')

    return render_template('user/horaire.html', **locals())


@prefix_param.route('/horaire/edit/<objectid:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'user_horaire')], ['edit'])
def horaire_edit(user_id):

    user = Users.objects.get(id=user_id)

    horaire = Horaire()
    form = FormHoraire()

    success = False

    if form.validate_on_submit():

        horaire_exist = Horaire.objects(Q(date_start=datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())) & Q(user=user.id))

        if len(horaire_exist):
            success = False
            form.date_start.errors.append('Il existe un taux horaire applicable pour la meme date')
        else:
            horaire.date_start = function.datetime_convert(form.date_start.data)
            horaire.montant = float(form.montant.data)
            horaire.user = user
            horaire_id = horaire.save()

            if function.date_convert(form.date_start.data) == datetime.date.today():
                user.tauxH = float(form.montant.data)
                user.save()

            flash('Enregistement effectue avec succes', 'success')
            success = True

    return render_template('user/horaire_edit.html', **locals())


@prefix_param.route('/horaire/refresh')
def horaire_refresh():

    users = Users.objects()

    for user in users:
        horaires = Horaire.objects(user=user.id)

        taux = 0.0
        date1 = None
        id = None
        for horaire in horaires:
            if horaire.date_start.date() <= datetime.date.today():
                if not date1:
                    date1 = horaire.date_start
                    taux = horaire.montant
                    id = horaire.id
                else:
                    if date1 < horaire.date_start:
                        date1 = horaire.date_start
                        taux = horaire.montant
                        id = horaire.id
        user.tauxH = taux
        if id:
            user.tauxHApp = id
        user.save()

    if request.args.get('user_id'):
        return redirect(url_for('user_param.horaire', user_id=request.args.get('user_id')))
    else:
        return render_template('401.html')


@prefix_param.route('/horaire/delete/<objectid:horaire_id>/<objectid:user_id>')
@login_required
@roles_required([('super_admin', 'user_horaire')], ['delete'])
def delete_horaire(horaire_id, user_id):
    horaires = Horaire.objects.get(id=horaire_id)
    horaires.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('user_param.horaire', user_id=user_id))


### TRAITEMENT DES BUDGETS DES UTILISATEURS ###
@prefix_param.route('/budget/<objectid:user_id>')
def budget(user_id):
    menu = 'user'
    submenu = 'users'
    context = 'budget'
    title_page = 'Parametre - Utilisateurs'

    from ..budget.models_budget import Budget, BudgetPrestation

    user = Users.objects.get(id=user_id)



    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    limit = 10
    offset = ((page - 1) * 10)

    list_budget = []

    count = Budget.objects(user_id=user.id).count()
    budget_user = Budget.objects(user_id=user.id).skip(offset).limit(limit)

    datas = budget_user

    for budget in datas:
        data = {}

        data['disponible'] = 0
        data['year'] = budget.date_start.year
        if budget.heure:
            data['disponible'] = budget.heure

        budget_prest = BudgetPrestation.objects(
            budget_id = budget.id
        )

        data['budget_prestation'] = []

        for prestation in budget_prest:
            data2 = {}
            data2['id'] = prestation.prestation_id.id
            data2['prestation'] = prestation.prestation_id.libelle
            data2['sigle'] = prestation.prestation_id.sigle
            data2['time'] = prestation.heure

            data['budget_prestation'].append(data2)

        list_budget.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='Budget de l\'utilisateur')

    return render_template('user/budget.html', **locals())


@prefix_param.route('/formation/<objectid:user_id>')
def formation(user_id):

    menu = 'user'
    submenu = 'users'
    context = 'formation'
    title_page = 'Parametre - Utilisateurs'

    user = Users.objects.get(id=user_id)

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    limit = 10
    offset = ((page - 1) * 10)

    #id Prestatation Ferier, Conge et Absence
    from ..tache.models_tache import Tache, Prestation
    prest_formation = Prestation.objects(sigle='FOR').first()

    if prest_formation:

        count = Tache.objects(
            Q(user_id=user.id) & Q(officiel=True) & Q(prestation_id=prest_formation.id)
        ).count()
        datas = Tache.objects(
            Q(user_id=user.id) & Q(officiel=True) & Q(prestation_id=prest_formation.id)
        ).skip(offset).limit(limit).order_by('-date_start')

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Taches Formations')

    else:
        flash('Demandez a l\'administrateur de configurer au mieux les prestations de l\'application', 'warning')
        return redirect(url_for('dashboard.index'))

    return render_template('user/formation.html', **locals())


@prefix_param.route('/formation/detail/<objectid:tache_id>')
@login_required
def formation_detail(tache_id):

    from ..tache.models_tache import Tache

    menu = 'user'
    submenu = 'users'
    context = 'formation'
    title_page = 'Parametre - Utilisateurs'

    tache = Tache.objects.get(id=tache_id)

    return render_template('tache/detail.html', **locals())


@prefix_param.route('/formation/edit/<objectid:user_id>', methods=['GET', 'POST'])
@login_required
def hors_projet(user_id):

    from ..tache.models_tache import Tache, Projet, Prestation, Update_Tache
    from ..tache.forms_tache import FormTache

    hors_projet = True


    taches = Tache()
    form = FormTache()
    form.contact.data = None


    form.projet_id.choices = [('0', 'Selectionnez un projet')]
    for projet in Projet.objects(closed=False):
        form.projet_id.choices.append((str(projet.id), projet.titre))

    utilisateur = Users.objects().get(id=user_id)
    form.user_id.choices = [(str(utilisateur.id), utilisateur.first_name+" "+utilisateur.last_name)]

    if form.prestation_id.data:
        prest = Prestation.objects.get(id=form.prestation_id.data)
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'


    list_prestation = Prestation.objects(sigle='FOR')

    success = False
    if form.validate_on_submit():
        taches.titre = form.titre.data
        taches.description = form.description.data
        taches.heure = form.heure.data

        user = Users.objects.get(id=form.user_id.data)
        taches.user_id = user

        if form.facturable.data == '2':
            taches.facturable = False
        if form.facturable.data == '1':
            taches.facturable = True

        prestation = Prestation.objects.get(id=form.prestation_id.data)
        taches.prestation_id = prestation

        update = Update_Tache()
        time_zones = pytz.timezone('Africa/Douala')
        date_now = datetime.datetime.now(time_zones)
        the_user = Users.objects.get(id=session.get('user_id'))

        update.date = date_now
        update.user = the_user
        update.action = 'formation'

        update.notified = True

        taches.updated.append(update)

        taches.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        taches.officiel = True
        taches.save()
        success = True

    return render_template('user/edit_formation.html', **locals())


@prefix_param.route('/formation/delete/<objectid:user_id>/<objectid:tache_id>')
@login_required
def formation_delete(user_id, tache_id):

    from ..tache.models_tache import Tache


    taches = Tache.objects.get(id=tache_id)

    from ..user.models_user import Update_User
    userC = Users.objects.get(id=session.get('user_id'))

    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    save = False
    for action in taches.notified():
        if action.notified:
            dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(action.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            if dif.seconds >= 3600:
                save = True

    if save:
        update = Update_User()

        update.date = function.datetime_convert(date_now)
        update.user = str(taches.user_id.id)
        update.action = 'delete_tache'
        update.notified = True
        update.content = taches.titre

        userC.updated.append(update)
        userC.save()


    taches.delete()

    return redirect(url_for('user_param.formation', user_id=user_id))