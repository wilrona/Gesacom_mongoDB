__author__ = 'wilrona'

from ...modules import *
from ..role.models_role import Roles
from forms_role import FormRole


# Flask-Cache (configured to use App Engine Memcache API)
prefix = Blueprint('role', __name__)


@prefix.route('/role', methods=['GET', 'POST'])
def index():
    menu = 'societe'
    submenu = 'roles'
    context = 'role'
    title_page = 'Gestion des roles'

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

    count = Roles.objects(Q(valeur__ne='super_admin') & Q(parent=None)).count()
    datas = Roles.objects(Q(valeur__ne='super_admin') & Q(parent=None)).skip(offset).limit(limit)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='Roles')

    return render_template('role/index.html', **locals())


@prefix.route('/role/edit/<objectid:role_id>',  methods=['GET', 'POST'])
@login_required
def edit(role_id):

    roles = Roles.objects.get(id=role_id)
    form = FormRole(obj=roles)

    success = False
    if form.validate_on_submit():

        roles.description = form.description.data
        roles.active = form.active.data
        roles.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('role/edit.html', **locals())


@prefix.route('/role/list/<objectid:role_id>',  methods=['GET', 'POST'])
@login_required
def list(role_id):

    module = Roles.objects.get(id=role_id)
    roles = Roles.objects(
        parent = module.id
    )

    return render_template('role/list.html', **locals())


@prefix.route('/role/generate')
def generate():

    for mod in global_role:

        module_exite = Roles.objects(
            valeur = mod['valeur']
        )

        if not len(module_exite):
            module = Roles()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.save()
        else:
            module = module_exite.first()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.save()

        for rol in mod['role']:

            role_exist = Roles.objects(
                valeur =rol['valeur']
            )

            if not role_exist.count():
                role = Roles()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.save()
            else:
                role = role_exist.first()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.save()

    flash(u' All Role generated.', 'success')
    return redirect(url_for('role.index'))

