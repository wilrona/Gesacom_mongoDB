__author__ = 'Ronald'


from views_projet import *
from views_besoin import *

app.register_blueprint(prefix, url_prefix='/projet')
app.register_blueprint(prefix_besoin, url_prefix='/finance')
