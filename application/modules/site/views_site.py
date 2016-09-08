__author__ = 'Ronald'

from ...modules import *
from models_site import Site
from forms_site import FormSite
from ..societe.models_societe import Societe

prefix = Blueprint('site', __name__)


@prefix.route('/site')
@login_required
@roles_required([('super_admin', 'site')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'site'
    title_page = 'Parametre - Sites'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Site.objects()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='sites')
    datas.paginate(page=page, per_page=10)

    return render_template('site/index.html', **locals())


@prefix.route('/site/edit',  methods=['GET', 'POST'])
@prefix.route('/site/edit/<objectid:site_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'site')], ['edit'])
def edit(site_id=None):

    if site_id:
        sites = Site.objects().get(id=site_id)
        form = FormSite(obj=sites)
    else:
        sites = Site()
        form = FormSite()

    success = False
    if form.validate_on_submit():

        entreprise = Societe.objects().first()

        sites.libelle = form.libelle.data
        sites.societe = entreprise
        sites.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('site/edit.html', **locals())

@roles_required([('super_admin', 'site')], ['delete'])
@prefix.route('/site/delete/<objectid:site_id>')
def delete(site_id):
    sites = Site.objects.get(id=site_id)
    if not sites.count_user():
        sites.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('site.index'))