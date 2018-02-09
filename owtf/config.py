import json
import logging
import os
import warnings

import yaml
from flask import Flask, g
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
# Remove warnings
from sqlalchemy.exc import SAWarning
warnings.simplefilter('always', SAWarning)
logging.captureWarnings(True)

from owtf import get_revision
from owtf.constants import PROJECT_ROOT, OWTF_CONF, ROOT_DIR


alembic = Alembic()
db = SQLAlchemy()
sentry = Sentry(logging=True, level=logging.WARN)


def get_db_config():
    if os.environ.get("DOCKER", None):
        DATABASE_NAME = os.environ["POSTGRES_DB"]
        DATABASE_PASS = os.environ["POSTGRES_PASSWORD"]
        DATABASE_USER = os.environ["POSTGRES_USER"]
        DATABASE_IP = "db"
        DATABASE_PORT = 5342
    else:
        with open(os.path.join(OWTF_CONF, "db.yaml"), "r") as f:
            conf = yaml.load(f)
            DATABASE_PASS = conf["password"]
            DATABASE_NAME = conf['database_name']
            DATABASE_USER = conf['username']
            DATABASE_IP = conf['database_ip']
            DATABASE_PORT = int(conf['database_port'])

    uri = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(DATABASE_USER, DATABASE_PASS, DATABASE_IP, str(DATABASE_PORT),
                                                    DATABASE_NAME)
    return uri


def with_health_check(app):
    def middleware(environ, start_response):
        if environ.get('PATH_INFO', '') == '/health':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'ok': True})]
        return app(environ, start_response)
    return middleware


def create_app(_read_config=True, **config):
    app = Flask(
        __name__,
        static_folder=os.path.join(ROOT_DIR, 'webapp', 'build'),
        template_folder=os.path.join(ROOT_DIR, 'templates')
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_config()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL') or 'INFO'

    if _read_config:
        if os.environ.get('OWTF_CONF'):
            app.config.from_envvar('OWTF_CONF')
        else:
            # Look for $HOME/.owtf/owtf.conf.py
            app.config.from_pyfile(os.path.join(OWTF_CONF, 'owtf.conf.py'), silent=True)

    app.wsgi_app = with_health_check(app.wsgi_app)
    app.config.update(config)

    if app.config.get('LOG_LEVEL'):
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))

    # init sentry first
    sentry.init_app(app)
    # https://github.com/getsentry/raven-python/issues/1030
    from raven.handlers.logging import SentryHandler
    app.logger.addHandler(SentryHandler(client=sentry.client, level=logging.WARN))

    configure_db(app)
    #configure_api(app)
    #configure_web(app)

    from . import models

    return app


def configure_db(app):
    from sqlalchemy import event
    from sqlalchemy.orm import mapper
    from sqlalchemy.inspection import inspect

    alembic.init_app(app)
    db.init_app(app)

    @event.listens_for(mapper, "init")
    def instant_defaults_listener(target, args, kwargs):
        for key, column in inspect(type(target)).columns.items():
            if column.default is not None:
                if callable(column.default.arg):
                    setattr(target, key, column.default.arg(target))
                else:
                    setattr(target, key, column.default.arg)

    event.listen(mapper, 'init', instant_defaults_listener)


def configure_api(app):
    from owtf import api
    app.register_blueprint(api.app, url_prefix='/api')


def configure_web(app):
    from owtf.web.auth import AuthorizedView, LoginView, LogoutView

    # the path used by the webapp for static resources uses the current app
    # version (which is a git hash) so that browsers don't use an old, cached
    # versions of those resources

    if app.debug:
        static_root = os.path.join(PROJECT_ROOT, 'static')
        revision = '0'
    else:
        static_root = os.path.join(PROJECT_ROOT, 'static-built')
        revision_facts = get_revision or {}
        revision = revision_facts.get('hash', '0')

    app.add_url_rule('/auth/login/', view_func=LoginView.as_view('login', authorized_url='authorized'))
    app.add_url_rule('/auth/logout/', view_func=LogoutView.as_view('logout', complete_url='index'))
    app.add_url_rule('/auth/complete/', view_func=AuthorizedView.as_view('authorized', complete_url='index',
                                                                         authorized_url='authorized'))

    configure_default(app)
    if app.debug:
        from owtf.web import debug
        app.register_blueprint(debug.app, url_prefix='/debug')



def configure_default(app):
    from owtf.web.index import IndexView

    static_root = os.path.join(PROJECT_ROOT, 'webapp')
    revision_facts = get_revision or {}
    revision = revision_facts.get('hash', '0') if not app.debug else '0'

    app.add_url_rule('/<path:path>', view_func=IndexView.as_view('index-path'))
    app.add_url_rule('/', view_func=IndexView.as_view('index'))
