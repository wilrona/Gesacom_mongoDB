__author__ = 'Ronald'


from views_upload import *
from views_mail import *

app.register_blueprint(prefix, url_prefix="/upload")
app.register_blueprint(prefix_cron, url_prefix="/cron")