__author__ = 'Ronald'

from ...modules import *


from ..tache.models_tache import Tache, Projet, Users
from ..client.models_client import Client
from ..domaine.models_domaine import Domaine, Service
from models_projet import FraisProjet
from forms_projet import FormProjet

prefix = Blueprint('projet', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'projet')])
def index():
    menu = 'projet'
    submenu = 'tous'
    context = ''
    title_page = 'Projets'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1


    count = Projet.objects(Q(closed=False) & Q(suspend=False)).count()

    limit = 25
    offset = ((page - 1) * 25)


    datas = Projet.objects(
        Q(closed=False) & Q(suspend=False)
    ).skip(offset).limit(limit)

    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'suspend':
            count = Projet.objects(Q(closed=False) & Q(suspend=True)).count()
            datas = Projet.objects(
                 Q(closed=False) & Q(suspend=True)
            ).skip(offset).limit(limit)
            small_title = 'en suspend'

        if request.args.get('filtre') == 'cloture':
            count = Projet.objects(Q(closed=True) & Q(suspend=False)).count()
            datas = Projet.objects(
                 Q(closed=True) & Q(suspend=False)
            ).skip(offset).limit(limit)
            small_title = 'clotures'

    pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Projets')

    return render_template('projet/index.html', **locals())



@prefix.route('/demande')
@login_required
@roles_required([('super_admin', 'projet_demande')])
def index_demande():
    menu = 'projet'
    submenu = 'demande'
    context = ''
    title_page = 'demandes projets'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1


    count = Projet.objects(Q(attente=True) & Q(rejet=False)).count()

    offset = 0
    limit = 25
    if page > 1:
        offset = ((page - 1) * 25)


    datas = Projet.objects(Q(attente=True) & Q(rejet=False)).skip(offset).limit(limit)

    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'rejet':
            count = Projet.objects(Q(attente=False) & Q(rejet=True)).count()
            datas = Projet.objects(Q(attente=False) & Q(rejet=True)).skip(offset).limit(limit)
            small_title = 'Rejetee'


    pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Projets')

    return render_template('projet/index_demande.html', **locals())

@prefix.route('/me')
def me():

    menu = 'projet'
    submenu = 'my'
    context = ''
    title_page = 'Projets'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    user = Users.objects.get(id=session.get('user_id'))
    admin_user = Users.objects(email="admin@accentcom-cm.com").first()

    all_tache = []
    for tache in Tache.objects(user_id=user.id):
        if tache.projet_id:
            all_tache.append(tache.projet_id.id)

    count = Projet.objects(Q(responsable_id=user.id) & Q(suspend=False) & Q(closed=False)).count()


    limit = 25
    offset = ((page - 1) * 25)


    responsable = Projet.objects(
        Q(responsable_id=user.id) & Q(suspend=False) & Q(closed=False)
    ).skip(offset).limit(limit)

    all_projet = []
    all_projet_id = []
    en_cours = Projet.objects(
        Q(closed=False) & Q(suspend=False)
    )

    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'suspend':
            en_cours = Projet.objects(
                Q(closed=False) & Q(suspend=True)
            )

            count = Projet.objects(Q(closed=True) & Q(suspend=False) & Q(responsable_id=user.id)).count()

            responsable = Projet.objects(
                Q(closed=True) & Q(suspend=False) & Q(responsable_id=user.id)
            ).skip(offset).limit(limit)

            small_title = 'en suspend'

        if request.args.get('filtre') == 'cloture':
            en_cours = Projet.objects(
                 Q(closed=True) & Q(suspend=False)
            )
            count = Projet.objects(Q(closed=False) & Q(suspend=True) & Q(responsable_id=user.id)).count()


            responsable = Projet.objects(
                Q(closed=False) & Q(suspend=True) & Q(responsable_id=user.id)
            ).skip(offset).limit(limit)

            small_title = 'clotures'

    for resp in responsable:
        if resp.id not in all_tache:
            all_tache.append(resp.id)

    # Projet ou l'utilisateur a une tache
    for proj in en_cours:
        if proj.id in all_tache:
            projet = {}
            projet['id'] = proj.id
            projet['code'] = proj.code
            projet['titre'] = proj.titre
            projet['client'] = proj.client_id.name
            projet['responsable'] = proj.responsable_id.last_name
            projet['responsable_id'] = str(proj.responsable_id.id)
            projet['attente'] = proj.attente
            all_projet.append(projet)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='Projet')

    return render_template('projet/me.html', **locals())


@prefix.route('/edit', methods=['GET', 'POST'])
@prefix.route('/edit/<objectid:projet_id>', methods=['GET', 'POST'])
@login_required
def edit(projet_id=None):
    menu = 'projet'
    submenu = 'projet'
    context = 'information'
    title_page = 'Projets - Edition'

    if projet_id:
        projet = Projet.objects.get(id=projet_id)
        form = FormProjet(obj=projet)
        if request.method != 'POST':

            form.domaine_id.data = str(projet.domaine_id.id)
            form.service_id.data = str(projet.service_id.id)
            form.client_id.data = str(projet.client_id.id)
            form.responsable_id.data = str(projet.responsable_id.id)
            if projet.prospect_id:
                form.prospect_id.data = str(projet.prospect_id.id)
            form.id.data = projet_id

    else:
        projet = Projet()
        form = FormProjet()

    form.domaine_id.choices = [(0, 'Selection du domaine')]
    for domaine in Domaine.objects():
        form.domaine_id.choices.append((str(domaine.id), domaine.libelle))

    service = []
    if projet_id:
        services = Service.objects(
            domaine=projet.domaine_id.id
        )
        prospects = Client.objects(
            prospect=True
        )

    # if form.domaine_id.data and not projet_id:
    #     domaine = Domaine.objects.get(id=form.domaine_id.data)
    #     services = Service.objects(
    #         domaine=domaine.id
    #     )

    if not projet_id:
        prospects = Client.objects(
            prospect=True
        )


    form.client_id.choices = [(0, 'Selection du client')]
    for client in Client.objects(prospect=False):
        form.client_id.choices.append((str(client.id), client.name))

    form.responsable_id.choices = [(0, 'Selection du responsable')]
    for user in Users.objects(email__ne='admin@accentcom-cm.com'):
        form.responsable_id.choices.append((str(user.id), user.first_name+" "+user.last_name))

    if form.validate_on_submit() and current_user.has_roles([('super_admin', 'projet')], ['edit']):

        projet.titre = form.titre.data

        client_code = Client.objects.get(id=form.client_id.data)
        if not projet_id:
            projet_client = Projet.objects(
                client_id= client_code.id
            )
            projet.code = client_code.ref+""+str(len(projet_client)+1)

        projet.heure = form.heure.data
        projet.montant = float(form.montant.data)
        projet.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        projet.date_end = datetime.datetime.combine(function.date_convert(form.date_end.data), datetime.datetime.min.time())
        projet.client_id = client_code

        if client_code.myself and int(form.prospect_id.data):
            pros = Client.objects.get(id=form.prospect_id.data)
            projet.prospect_id = pros

        user = Users.objects.get(id=form.responsable_id.data)
        projet.responsable_id = user

        domaine = Domaine.objects.get(id=form.domaine_id.data)
        projet.domaine_id = domaine

        service = Service.objects.get(id=form.service_id.data)
        projet.service_id = service

        if not projet_id:
            projet.facturable = form.facturable.data

        projet.closed = form.closed.data

        projet_id = projet.save()
        flash('Enregistrement effectue avec succes', 'success')
        return redirect(url_for('projet.edit', projet_id=projet_id.id))

    return render_template('projet/edit.html', **locals())


@prefix.route('/demande/edit', methods=['GET', 'POST'])
@prefix.route('/demande/edit/<objectid:projet_id>', methods=['GET', 'POST'])
@login_required
def edit_demande(projet_id=None):
    menu = 'projet'
    submenu = 'projet'
    context = 'information'
    title_page = 'Demandes Projets - Edition'

    demande = True
    user = True

    if projet_id:
        projet = Projet.objects.get(id=projet_id)

        if not projet.attente and not projet.rejet:
            return redirect(url_for('projet.edit', projet_id=projet_id))

        form = FormProjet(obj=projet)
        if request.method != 'POST':

            form.domaine_id.data = str(projet.domaine_id.id)
            form.service_id.data = str(projet.service_id.id)
            form.client_id.data = str(projet.client_id.id)
            form.responsable_id.data = str(projet.responsable_id.id)
            if projet.prospect_id:
                form.prospect_id.data = str(projet.prospect_id.id)
            form.id.data = projet_id

    else:
        projet = Projet()
        form = FormProjet()

    form.domaine_id.choices = [(0, 'Selection du domaine')]
    for domaine in Domaine.objects():
        form.domaine_id.choices.append((str(domaine.id), domaine.libelle))

    services = []
    if projet_id:
        services = Service.objects(
            domaine=projet.domaine_id.id
        )
        prospects = Client.objects(
            prospect=True
        )

    # if form.domaine_id.data and not projet_id:
    #     domaine = Domaine.objects.get(id=form.domaine_id.data)
    #     services = Service.objects(
    #         domaine=domaine.id
    #     )

    if not projet_id:
        prospects = Client.objects(
            prospect=True
        )


    form.client_id.choices = [(0, 'Selection du client')]
    for client in Client.objects(prospect=False):
        form.client_id.choices.append((str(client.id), client.name))

    if current_user.has_roles([('super_admin', 'projet_demande')], ['edit']):
        form.responsable_id.choices = [(0, 'Selection du responsable')]
        for user in Users.objects(email__ne='admin@accentcom-cm.com'):
            form.responsable_id.choices.append((str(user.id), user.first_name+" "+user.last_name))
    else:
        current_users = Users.objects.get(id=session.get('user_id'))
        form.responsable_id.choices = [(str(current_users.id), current_users.first_name+" "+current_users.last_name)]
        demande = False

    if form.validate_on_submit():

        projet.titre = form.titre.data

        client_code = Client.objects.get(id=form.client_id.data)

        projet.heure = form.heure.data
        projet.montant = float(form.montant.data)
        projet.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        projet.date_end = datetime.datetime.combine(function.date_convert(form.date_end.data), datetime.datetime.min.time())
        projet.client_id = client_code

        if client_code.myself and int(form.prospect_id.data):
            pros = Client.objects.get(id=form.prospect_id.data)
            projet.prospect_id = pros

        user = Users.objects.get(id=form.responsable_id.data)
        projet.responsable_id = user

        domaine = Domaine.objects.get(id=form.domaine_id.data)
        projet.domaine_id = domaine

        service = Service.objects.get(id=form.service_id.data)
        projet.service_id = service

        if not projet_id:
            projet.facturable = form.facturable.data

        projet.closed = form.closed.data

        projet.attente = True
        projet.rejet = False

        projet_id = projet.save()
        flash('Enregistrement effectue avec succes', 'success')
        return redirect(url_for('projet.edit_demande', projet_id=projet_id.id))

    return render_template('projet/demande_edit.html', **locals())


@prefix.route('/demande/valide/<objectid:projet_id>')
def valide_demande(projet_id):
    projet = Projet.objects.get(id=projet_id)

    if projet.attente:
        projet_client = Projet.objects(
                Q(client_id=projet.client_id.id) & Q(code__ne=None)
        )
        projet.code = projet.client_id.ref+""+str(len(projet_client)+1)
        projet.attente = False
    else:
        projet.attente = True
    projet.save()
    flash('Projet validee avec success', 'success')

    return redirect(url_for('projet.edit', projet_id=projet_id))


@prefix.route('/demande/rejet/<objectid:projet_id>')
def rejet_demande(projet_id):
    projet = Projet.objects.get(id=projet_id)

    if projet.rejet:
        projet.attente = True
        projet.rejet = False
    else:
        projet.rejet = True
        projet.attente = False

    projet.save()
    flash('Projet rejete avec success', 'success')

    return redirect(url_for('projet.edit_demande', projet_id=projet_id))


@prefix.route('/closed/<objectid:projet_id>')
def closed(projet_id):
    projet = Projet.objects.get(id=projet_id)

    if projet.closed:
        projet.closed = False
        projet.save()
    else:
        tache_exist = Tache.objects(
            projet_id == projet.id
        )

        tache_closed = Tache.objects(
            Q(projet_id=projet.id) & Q(closed=True)
        )

        if len(tache_closed) == len(tache_exist):
            projet.closed = True
            projet.save()
        else:
            flash('Impossible de cloturer ce projet car il y\'a des taches non cloturees existantes', 'warning')

    return redirect(url_for('projet.edit', projet_id=projet_id))


@prefix.route('/suspend/<objectid:projet_id>')
def suspend(projet_id):

    projet = Projet.objects.get(id=projet_id)

    if projet.suspend:
        projet.suspend = False
    else:
        projet.suspend = True
    projet.save()

    return redirect(url_for('projet.edit', projet_id=projet_id))


@prefix.route('/delete/<objectid:projet_id>')
@login_required
@roles_required([('super_admin', 'projet')], ['edit'])
def delete(projet_id):

    projet = Projet.objects.get(id=projet_id)

    frais = FraisProjet.objects(
        projet_id=projet.id
    )

    tache = Tache.objects(
        projet_id=projet.id
    )

    if frais or tache:
        flash('Impossible de supprimer le projet '+ str(projet.code), 'danger')
    else:
        flash('Suppression effectue avec succes', 'success')
        projet.delete()
    return redirect(url_for('projet.index'))


@prefix.route('/service')
@prefix.route('/service/<domaine_id>')
def services(domaine_id = None):
    data = {}
    if domaine_id:
        domaine = Domaine.objects.get(id=domaine_id)
        service = Service.objects(
            domaine= domaine.id
        )
        for ser in service:
            data[str(ser.id)] = ser.libelle
    resp = jsonify(data)
    return resp


@prefix.route('/prospect')
@prefix.route('/prospect/<client_id>')
def prospects(client_id = None):
    data = {}
    if client_id:
        client = Client.objects.get(id=client_id)
        if client.myself:
            clients = Client.objects(
                prospect=True
            )
            for cli in clients:
                data[str(cli.id)] = cli.name
    resp = jsonify(data)
    return resp

