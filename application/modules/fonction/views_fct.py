__author__ = 'Ronald'

from ...modules import *
from models_fct import Fonction
from forms_fct import FormFonction


prefix = Blueprint('fonction', __name__)


@prefix.route('/fonction')
@login_required
@roles_required([('super_admin', 'fonction')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'fonction'
    title_page = 'Parametre - Fonctions'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Fonction.objects()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='fonctions')
    datas.paginate(page=page, per_page=10)

    return render_template('fonction/index.html', **locals())


@prefix.route('/fonction/edit',  methods=['GET', 'POST'])
@prefix.route('/fonction/edit/<objectid:fonction_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'fonction')], ['edit'])
def edit(fonction_id=None):

    if fonction_id:
        grades = Fonction.objects.get(id=fonction_id)
        form = FormFonction(obj=grades)
    else:
        grades = Fonction()
        form = FormFonction()

    success = False
    if form.validate_on_submit():

        grades.libelle = form.libelle.data
        grades.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('fonction/edit.html', **locals())


@prefix.route('/fonction/delete/<objectid:fonction_id>')
@login_required
@roles_required([('super_admin', 'fonction')], ['edit'])
def delete(fonction_id):
    fonctions = Fonction.objects.get(id=fonction_id)
    if not fonctions.count():
        fonctions.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('fonction.index'))