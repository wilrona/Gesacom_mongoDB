__author__ = 'Ronald'


from ...modules import *
from forms_societe import FormSociete
from models_societe import Societe


prefix = Blueprint('societe', __name__)


@prefix.route('/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'entreprise')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'information'
    title_page = 'Parametre - Entreprises'

    form = FormSociete()

    if request.method == 'GET':
        entreprise = Societe.objects.first()
        if entreprise:
            form = FormSociete(obj=entreprise)
    else:
        form = FormSociete(request.form)
        entreprise = Societe.objects.first()
        if not entreprise:
            entreprise = Societe()

    list_contry = global_list_country

    if form.validate_on_submit() and request.method == 'POST' and current_user.has_roles([('super_admin','entreprise')], ['edit']):

        entreprise.typEnt = form.typEnt.data
        entreprise.name = form.name.data
        entreprise.slogan = form.slogan.data
        entreprise.bp = form.bp.data
        entreprise.adress = form.adress.data
        entreprise.pays = form.pays.data
        entreprise.ville = form.ville.data
        entreprise.phone = form.phone.data
        entreprise.capital = form.capital.data
        entreprise.numcontr = form.numcontr.data
        entreprise.registcom = form.registcom.data
        entreprise.email = form.email.data
        entreprise.siteweb = form.siteweb.data
        entreprise.save()

        flash(u"Enregistrement/Modification effectue avec succes", 'success')
        # return redirect(url_for('societe.index'))

    return render_template('societe/index.html', **locals())
