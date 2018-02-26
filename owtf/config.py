import json
import warnings
import os
from collections import defaultdict
import logging
try: #PY3
    from urllib.parse import urlparse
except ImportError:  #PY2
     from urlparse import urlparse
try:
    import configparser as parser
except ImportError:
    import ConfigParser as parser

import yaml
from flask import Flask
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
# Remove warnings
from sqlalchemy.exc import SAWarning
warnings.simplefilter('always', SAWarning)
logging.captureWarnings(True)

from owtf.constants import ROOT_DIR, REPLACEMENT_DELIMITER, CONFIG_TYPES
from owtf.lib.exceptions import PluginAbortException
from owtf import get_revision
from owtf.constants import PROJECT_ROOT, OWTF_CONF, ROOT_DIR
from owtf.api import APIController, APICatchall


alembic = Alembic()
db = SQLAlchemy()
sentry = Sentry(logging=True, level=logging.WARN)
api = APIController(prefix='/api/0')


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

    @app.before_request
    def capture_user(*args, **kwargs):
        from owtf.api.auth import get_current_user
        user = get_current_user()
        if user is not None:
            sentry.client.user_context({
                'id': user.id,
                'email': user.email,
            })

    api.init_app(app)
    configure_db(app)
    configure_api()
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


def configure_api():
    from owtf.api.config import Configuration
    from owtf.api.plugin import PluginData, PluginOutput, PluginNameOutput
    from owtf.api.report import ReportExport
    from owtf.api.session import OWTFSession
    from owtf.api.targets import TargetConfig, TargetConfigSearch
    from owtf.api.transactions import TransactionData, TransactionHrt, TransactionSearch
    from owtf.api.work import Worker, Worklist, WorklistSearch

    api.add_resource(Configuration, '/configuration/')
    api.add_resource(PluginNameOutput, '/targets/<target_id>/poutput/names/')
    api.add_resource(PluginData, '/plugins/')
    api.add_resource(PluginOutput, '/targets/<target_id>/poutput/')
    api.add_resource(ReportExport, '/targets/<target_id>/export/')
    api.add_resource(OWTFSession, '/sessions/<target_id>/')
    api.add_resource(TargetConfigSearch, '/targets/search/')
    api.add_resource(TargetConfig, '/targets/<target_id>/')
    api.add_resource(TransactionData, '/targets/<target_id>/transactions/<transaction_id>/')
    api.add_resource(TransactionHrt, '/targets/<target_id>/transactions/hrt/<transaction_id>/')
    api.add_resource(TransactionSearch, '/targets/<target_id>/transactions/search/')
    api.add_resource(WorklistSearch, '/worklist/search/')
    api.add_resource(Worker, '/workers/<worker_id>/')
    api.add_resource(Worklist, '/worklist/<work_id>/')
    api.add_resource(APICatchall, '/<path:path>')


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


class Config(object):

    profiles = {
        "GENERAL_PROFILE": None,
        "RESOURCES_PROFILE": None,
        "WEB_PLUGIN_ORDER_PROFILE": None,
        "NET_PLUGIN_ORDER_PROFILE": None,
        "MAPPING_PROFILE": None
    }
    target = None

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.owtf_pid = os.getppid()
        self.config = defaultdict(list)  # General configuration information.
        for type in CONFIG_TYPES:
            self.config[type] = {}        # key can consist alphabets, numbers, hyphen & underscore.
        self.cli_options = {}

    def is_set(self, key):
        """Checks if the key is set in the config dict

        :param key: Key to check
        :type key: `str`
        :return: True if present, else False
        :rtype: `bool`
        """
        key = self.pad_key(key)
        config = self.get_config_dict()
        for type in CONFIG_TYPES:
            if key in config[type]:
                return True
        return False

    def get_key_val(self, key):
        """Gets the right config for target / general.

        :param key: The key
        :type key: `str`
        :return: Value for the key
        """
        config = self.get_config_dict()
        for type in CONFIG_TYPES:
            if key in config[type]:
                return config[type][key]

    def pad_key(self, key):
        """Add delimiters.

        :param key: Key to pad
        :type key: `str`
        :return: Padded key string
        :rtype: `str`
        """
        return REPLACEMENT_DELIMITER + key + REPLACEMENT_DELIMITER

    def strip_key(self, key):
        """Replaces key with empty space

        :param key: Key to clear
        :type key: `str`
        :return: Empty key
        :rtype: `str`
        """
        return key.replace(REPLACEMENT_DELIMITER, '')

    def get_val(self, key):
        """Transparently gets config info from target or General.

        :param key: Key
        :type key: `str`
        :return: The value for the key
        """
        try:
            key = self.pad_key(key)
            return self.get_key_val(key)
        except KeyError:
            message = "The configuration item: %s does not exist!" % key
            # Raise plugin-level exception to move on to next plugin.
            raise PluginAbortException(message)

    def get_as_list(self, key_list):
        """Get values for keys in a list

        :param key_list: List of keys
        :type key_list: `list`
        :return: List of corresponding values
        :rtype: `list`
        """
        value_list = []
        for key in key_list:
            value_list.append(self.get_val(key))
        return value_list

    def get_header_list(self, key):
        """Get list from a string of values for a key

        :param key: Key
        :type key: `str`
        :return: List of values
        :rtype: `list`
        """
        return self.get_val(key).split(',')

    def set_general_val(self, type, key, value):
        """ Set value for a key in any config file

        :param type: Type of config file, framework or general.cfg
        :type type: `str`
        :param key: The key
        :type key: `str`
        :param value: Value to be set
        :type value:
        :return: None
        :rtype: None
        """
        self.config[type][key] = value

    def set_val(self, key, value):
        """set config items in target-specific or General config."""
        # Store config in "replacement mode", that way we can multiple-replace
        # the config on resources, etc.
        key = REPLACEMENT_DELIMITER + key + REPLACEMENT_DELIMITER
        type = 'other'
        # Only when value is a string, store in replacements config.
        if isinstance(value, str):
            type = 'string'
        return self.set_general_val(type, key, value)

    def get_framework_config_dict(self):
        return self.get_config_dict()['string']

    def __getitem__(self, key):
        return self.get_val(key)

    def __setitem__(self, key, value):
        return self.set_val(key, value)

    def get_config_dict(self):
        """Get the global config dictionary

        :return: None
        :rtype: None
        """
        return self.config

    def get_replacement_dict(self):
        return {"FRAMEWORK_DIR": self.root_dir}

    def show(self):
        """Print all keys and values from configuration dictionary

        :return: None
        :rtype: None
        """
        logging.info("Configuration settings: ")
        for k, v in list(self.get_config_dict().items()):
            logging.info("%s => %s" % (str(k), str(v)))


config_handler = Config()
