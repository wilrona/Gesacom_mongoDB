__author__ = 'Ronald'

from ...modules import *
from models_dep import Departement
from forms_dep import FormDep
from ..societe.models_societe import Societe


prefix = Blueprint('departement', __name__)


@prefix.route('/departement')
@login_required
@roles_required([('super_admin', 'departement')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'departement'
    title_page = 'Parametre - Departements'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Departement.objects()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='departements')
    datas.paginate(page=page, per_page=10)

    return render_template('departement/index.html', **locals())


@prefix.route('/departement/edit',  methods=['GET', 'POST'])
@prefix.route('/departement/edit/<objectid:dep_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'departement')], ['edit'])
def edit(dep_id=None):

    if dep_id:
        departements = Departement.objects.get(id=dep_id)
        form = FormDep(obj=departements)
    else:
        departements = Departement()
        form = FormDep()

    if form.validate_on_submit():
        entreprise = Societe.objects.first()

        departements.libelle = form.libelle.data
        departements.societe = entreprise
        departements.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('departement/edit.html', **locals())


@prefix.route('/departement/delete/<objectid:dep_id>')
@login_required
@roles_required([('super_admin', 'departement')], ['delete'])
def delete(dep_id):
    departements = Departement.get_by_id(dep_id)
    if not departements.count_user():
        departements.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('departement.index'))