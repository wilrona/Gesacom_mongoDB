"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
# from application.modules import home, dashboard

from application.modules import home, dashboard, user, societe, site, departement, grade, fonction, frais, domaine, profil, \
    prestation, role, budget, charge, client, projet, tache, temps, rapport, conge, upload


# app.register_blueprint(home.prefix) # pas de url prefix pour la page d'accueil
# app.register_blueprint(dashboard.prefix, url_prefix='/dashboard')
#
# app.register_blueprint(role.prefix, url_prefix='/parametre')
# app.register_blueprint(profil.prefix, url_prefix='/parametre')
# app.register_blueprint(societe.prefix, url_prefix='/parametre')
# app.register_blueprint(grade.prefix, url_prefix='/parametre')
# app.register_blueprint(fonction.prefix, url_prefix='/parametre')
# app.register_blueprint(domaine.prefix, url_prefix='/parametre')
# app.register_blueprint(departement.prefix, url_prefix='/parametre')
#
# app.register_blueprint(charge.prefix, url_prefix='/parametre')
# app.register_blueprint(budget.prefix, url_prefix='/parametre')
#
# app.register_blueprint(frais.prefix, url_prefix='/parametre')
# app.register_blueprint(frais.prefix_projet, url_prefix="/projet")
# app.register_blueprint(frais.prefix_tache, url_prefix="/tache")
# #
# app.register_blueprint(user.prefix, url_prefix='/user')
# app.register_blueprint(user.prefix_param, url_prefix='/parametre')
# #
# app.register_blueprint(site.prefix, url_prefix='/parametre')
# #
# app.register_blueprint(temps.prefix_tache, url_prefix='/tache')
# app.register_blueprint(temps.prefix_tache_breack, url_prefix='/tache')
# app.register_blueprint(temps.prefix, url_prefix='/temps')
# #
# #
# app.register_blueprint(tache.prefix_projet, url_prefix='/projet')
# app.register_blueprint(tache.prefix, url_prefix='/tache')
# #
# app.register_blueprint(projet.prefix, url_prefix='/projet')
# #
# app.register_blueprint(prestation.prefix, url_prefix='/parametre')
# #
# app.register_blueprint(client.prefix, url_prefix='/client')
# app.register_blueprint(client.prefix_contact, url_prefix='/contact')
# #
# app.register_blueprint(conge.prefix, url_prefix='/permission')
# app.register_blueprint(conge.prefix_param, url_prefix='/parametre')
# #
# app.register_blueprint(rapport.prefix, url_prefix='/statistiques')
# #
# app.register_blueprint(upload.prefix, url_prefix="/upload")

## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/Unauthorized')
def server_Unauthorized():
    return render_template('401.html'), 401



