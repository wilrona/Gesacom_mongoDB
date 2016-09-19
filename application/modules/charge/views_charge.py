__author__ = 'Ronald'

from ...modules import *
from models_charge import Charge, Societe
from forms_charge import FormCharge

prefix = Blueprint('charge', __name__)


@prefix.route('/charge')
@login_required
@roles_required([('super_admin', 'charge')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'charge'
    title_page = 'Parametre - Charges/Impots'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    offset = 0
    limit = 25
    if page > 1:
        offset = ((page - 1) * 25)

    datas = Charge.objects().skip(offset).limit(limit)
    count = Charge.objects().count()

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='Charges')

    return render_template('charge/index.html', **locals())


@prefix.route('/charge/edit',  methods=['GET', 'POST'])
@prefix.route('/charge/edit/<objectid:charge_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(charge_id=None):

    if charge_id:
        charges = Charge.objects.get(id=charge_id)
        form = FormCharge(obj=charges)
    else:
        charges = Charge()
        form = FormCharge()

    success = False
    if form.validate_on_submit():
        entreprise = Societe.objects.first()

        charges.libelle = form.libelle.data
        charges.societe = entreprise
        charges.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('charge/edit.html', **locals())


@prefix.route('/charge/delete/<objectid:charge_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(charge_id):
    charges = Charge.objects.get(id=charge_id)

    from ..budget.models_budget import ChargeBudget
    bugdet = ChargeBudget.objects(
        charge_id=charges.id
    )

    if len(bugdet):
        flash('Impossible de supprimer cet element', 'warning')
    else:
        charges.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('charge.index'))