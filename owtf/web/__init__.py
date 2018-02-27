from flask import Blueprint

from owtf.web.index import index


app = Blueprint('web', __name__)

app.add_url_rule('/<path:path>', view_func=index)
app.add_url_rule('/', 'index', view_func=index)
