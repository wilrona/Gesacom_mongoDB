__author__ = 'Ronald'

from ...modules import *
from models_domaine import Domaine, Service
from forms_domaine import FormDomaine, FormService

prefix = Blueprint('domaine', __name__)


@prefix.route('/domaine')
@login_required
@roles_required([('super_admin', 'domaine')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'domaine'
    title_page = 'Parametre - Domaines'

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

    count = Domaine.objects().count()
    datas = Domaine.objects().skip(offset).limit(limit)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='domaines')

    return render_template('domaine/index.html', **locals())


@prefix.route('/domaine/edit',  methods=['GET', 'POST'])
@prefix.route('/domaine/edit/<objectid:domaine_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'domaine')], ['edit'])
def edit(domaine_id=None):

    if domaine_id:
        domaines = Domaine.objects.get(id=domaine_id)
        form = FormDomaine(obj=domaines)
        form.id.data = domaine_id
    else:
        domaines = Domaine()
        form = FormDomaine()

    success = False
    if form.validate_on_submit():

        domaines.libelle = form.libelle.data
        domaines.code = form.code.data
        domaines.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('domaine/edit.html', **locals())


@prefix.route('/domaine/delete/<objectid:domaine_id>')
@login_required
@roles_required([('super_admin', 'domaine')], ['delete'])
def delete(domaine_id):
    from ..projet.models_projet import Projet
    domaines = Domaine.objects.get(id=domaine_id)

    dom_projet = Projet.objects(
        domaine_id == domaines.id
    )

    if len(dom_projet):
        flash('Impossible de supprimer cet element', 'danger')
    else:
        domaines.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('domaine.index'))


@prefix.route('/domaine/service/<objectid:domaine_id>')
@login_required
@roles_required([('super_admin', 'ligne')])
def domaine_service(domaine_id):

    domaines = Domaine.objects.get(id=domaine_id)
    data_service = Service.objects(
        domaine=domaines.id
    )
    return render_template('domaine/index_ligne.html', **locals())


@prefix.route('/domaine/service/edit/<objectid:domaine_id>', methods=['GET', 'POST'])
@prefix.route('/domaine/service/edit/<objectid:domaine_id>/<objectid:service_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'ligne')], ['edit'])
def domaine_service_edit(domaine_id, service_id=None):

    domaines = Domaine.objects.get(id=domaine_id)

    if service_id:
        services = Service.objects.get(id=service_id)
        form = FormService(obj=services)
        form.id.data = service_id
    else:
        services = Service()
        form = FormService()

    if form.validate_on_submit():

        services.libelle = form.libelle.data
        services.code = form.code.data
        services.domaine = domaines
        services.save()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('domaine.domaine_service', domaine_id=domaine_id))

    return render_template('domaine/edit_ligne.html', **locals())


@prefix.route('/domaine/service/delete/<objectid:domaine_id>/<objectid:service_id>')
@login_required
@roles_required([('super_admin', 'ligne')], ['delete'])
def domaine_service_delete(domaine_id, service_id):
    from ..projet.models_projet import Projet

    services = Service.objects.get(id=service_id)

    projet = Projet.objects(
        service_id = services.id
    )

    if len(projet):
        flash('Impossible de supprimer', 'danger')
    else:
        services.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('domaine.domaine_service', domaine_id=domaine_id))