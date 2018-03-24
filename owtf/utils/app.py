"""
owtf.utils.app
~~~~~~~~~~~~~~
"""

import tornado.web

from owtf.models.base.session import Session, get_db_engine


class Application(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        Session.configure(bind=get_db_engine())
        self.session = Session()
        self.sentry_client = kwargs.pop("sentry_client", None)
        super(Application, self).__init__(*args, **kwargs)
