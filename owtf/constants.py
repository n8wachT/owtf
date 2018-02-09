"""
owtf.constants
~~~~~~~~~~~~~~

Ranking constants used across the framework.
"""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

HOME_DIR = os.path.expanduser("~")
OWTF_CONF = os.path.join(HOME_DIR, ".owtf")
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
PLUGINS_DIR = os.path.join(ROOT_DIR, 'plugins')
TEMPLATES = os.path.join(ROOT_DIR, 'templates')
STATIC_ROOT = os.path.join(ROOT_DIR, 'webapp', 'build')

FILE_SERVER = "127.0.0.1"
FILE_SERVER_PORT = 8010

# `int` value of ranks
OWTF_UNRANKED = -1
OWTF_PASSING = 0
OWTF_INFO = 1
OWTF_LOW = 2
OWTF_MEDIUM = 3
OWTF_HIGH = 4
OWTF_CRITICAL = 5

# Maps `int` value of ranks with `string` value.
RANKS = {
    OWTF_UNRANKED: 'Unranked',
    OWTF_PASSING: 'Passing',
    OWTF_INFO: 'Informational',
    OWTF_LOW: 'Low',
    OWTF_MEDIUM: 'Medium',
    OWTF_HIGH: 'High',
    OWTF_CRITICAL: 'Critical',
}

# Proxy
BLACKLIST_COOKIES = ['_ga', '__utma', '__utmb', '__utmc', '__utmz', '__utmv']
WHITELIST_COOKIES = ""
PROXY_RESTRICTED_RESPONSE_HEADERS = [
    "Content-Length",
    "Content-Encoding",
    "Etag",
    "Transfer-Encoding",
    "Connection",
    "Vary",
    "Accept-Ranges",
    "Pragma"
]

PROXY_RESTRICTED_REQUEST_HEADERS = [
    "Connection",
    "Pragma",
    "Cache-Control",
    "If-Modified-Since"
]

OUTPUT_PATH = 'owtf_review'
AUX_OUTPUT_PATH = 'owtf_review/auxiliary'

# The name of the directories relative to output path
TARGETS_DIR = 'targets'
WORKER_LOG_DIR = 'logs'
# logs_dir can be both relative or absolute path ;)
LOGS_DIR = 'logs'
# Used for logging in OWTF
OWTF_LOG_FILE = '/tmp/owtf.log'

PROXY_LOG = '/tmp/owtf/proxy.log'

### UI
UI_SERVER_LOG = '/tmp/owtf/ui_server.log'
FILE_SERVER_LOG = '/tmp/owtf/file_server.log'

DATE_TIME_FORMAT = '%d/%m/%Y-%H:%M'
FORCE_OVERWRITE = True
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/15.0'
PROXY_CHECK_URL = 'http://www.google.ie'

### Memory
RESOURCE_MONITOR_PROFILER = 0
PROCESS_PER_CORE = 1
MIN_RAM_NEEDED = 20

### Interface Server
SERVER_ADDR = '0.0.0.0'
UI_SERVER_PORT = 8009

### HTTP_AUTH
HTTP_AUTH_HOST = None
HTTP_AUTH_USERNAME = None
HTTP_AUTH_PASSWORD = None
HTTP_AUTH_MODE = 'basic'


### OUTBOUND PROXY
USE_OUTBOUND_PROXY = False
OUTBOUND_PROXY_IP = ''
OUTBOUND_PROXY_PORT = ''
OUTBOUND_PROXY_AUTH = None

### Inbound Proxy Configuration
INBOUND_PROXY_IP = '127.0.0.1'
INBOUND_PROXY_PORT = 8008
INBOUND_PROXY_PROCESSES = 0
INBOUND_PROXY_CACHE_DIR = '/tmp/owtf/proxy-cache'
CA_CERT = os.path.join(OWTF_CONF, "proxy", "certs", "ca.crt")
CA_KEY = os.path.join(OWTF_CONF, "proxy", "certs", "ca.key")
CA_PASS_FILE = os.path.join(OWTF_CONF, 'proxy', "certs", "ca_pass.txt")
CERTS_FOLDER = os.path.join(OWTF_CONF, 'proxy', 'certs')


# IMP PATHS
WEB_TEST_GROUPS = os.path.join(OWTF_CONF, 'config', 'profiles', 'plugin_web', 'groups.cfg')
NET_TEST_GROUPS = os.path.join(OWTF_CONF, 'config', 'profiles', 'plugin_net', 'groups.cfg')
AUX_TEST_GROUPS = os.path.join(OWTF_CONF, 'config', 'profiles', 'plugin_aux', 'groups.cfg')

### Default profile settings
DEFAULT_GENERAL_PROFILE = os.path.join(OWTF_CONF, 'config', 'general.cfg')
DEFAULT_RESOURCES_PROFILE = os.path.join(OWTF_CONF, 'config', 'resources.cfg')
DEFAULT_MAPPING_PROFILE = os.path.join(OWTF_CONF, 'config', 'mappings.cfg')
DEFAULT_FRAMEWORK_CONFIG = os.path.join(OWTF_CONF, 'config', 'framework.cfg')
DEFAULT_WEB_PLUGIN_ORDER_PROFILE = os.path.join(OWTF_CONF, 'config', 'profiles', 'plugin_web', 'order.cfg')
DEFAULT_NET_PLUGIN_ORDER_PROFILE = os.path.join(OWTF_CONF, 'config', 'profiles', 'plugin_net', 'order.cfg')

### Fallback
FALLBACK_FRAMEWORK_CONFIG = os.path.join(ROOT_DIR, 'data', 'config', 'framework.cfg')
FALLBACK_WEB_TEST_GROUPS = os.path.join(ROOT_DIR, 'data', 'config', 'profiles', 'plugin_web', 'groups.cfg')
FALLBACK_NET_TEST_GROUPS = os.path.join(ROOT_DIR, 'data', 'config', 'profiles', 'plugin_net', 'groups.cfg')
FALLBACK_AUX_TEST_GROUPS = os.path.join(ROOT_DIR, 'data', 'config', 'profiles', 'plugin_aux', 'groups.cfg')
FALLBACK_PLUGINS_DIR = os.path.join(ROOT_DIR, 'data', 'plugins')
FALLBACK_GENERAL_PROFILE = os.path.join(ROOT_DIR, 'data', 'config', 'general.cfg')
FALLBACK_RESOURCES_PROFILE = os.path.join(ROOT_DIR, 'data', 'config', 'resources.cfg')
FALLBACK_MAPPING_PROFILE = os.path.join(ROOT_DIR, 'data' + 'config', 'mappings.cfg')
FALLBACK_WEB_PLUGIN_ORDER_PROFILE = os.path.join(ROOT_DIR, 'config', 'conf', 'profiles', 'plugin_web', 'order.cfg')
FALLBACK_NET_PLUGIN_ORDER_PROFILE = os.path.join(ROOT_DIR, 'config', 'conf', 'profiles', 'plugin_net', 'order.cfg')
