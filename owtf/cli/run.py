import os
import logging
import sys

import click
from flask import current_app

from owtf.cli.base import cli
from owtf.config import create_app
from owtf.lib import exceptions
from owtf.managers.config import load_framework_config_file, load_config_db_file
from owtf.managers.mapping import load_mappings_from_file
from owtf.managers.plugin import load_test_groups, load_plugins
from owtf.managers.resource import load_resources_from_file
from owtf.managers.session import _ensure_default_session
from owtf.managers.target import load_targets, TargetManager
from owtf.work.worker import WorkerManager
from owtf.work.worklist import load_works
from owtf.managers.plugin_handler import PluginHandler
from owtf.managers.plugin_params import PluginParams
from owtf.proxy.main import start_proxy
from owtf.utils.file import create_temp_storage_dirs, clean_temp_storage_dirs
from owtf.constants import WEB_TEST_GROUPS, AUX_TEST_GROUPS, NET_TEST_GROUPS, DEFAULT_RESOURCES_PROFILE, \
    FALLBACK_RESOURCES_PROFILE, FALLBACK_AUX_TEST_GROUPS, FALLBACK_NET_TEST_GROUPS, FALLBACK_WEB_TEST_GROUPS, \
    FALLBACK_MAPPING_PROFILE, DEFAULT_MAPPING_PROFILE, DEFAULT_FRAMEWORK_CONFIG, FALLBACK_FRAMEWORK_CONFIG, \
    DEFAULT_GENERAL_PROFILE, FALLBACK_GENERAL_PROFILE, ROOT_DIR


def process_args():
    args = ''
    if plugin_group == 'auxiliary':
        # For auxiliary plugins, the scope are the parameters.
        args = scope
        # auxiliary plugins do not have targets, they have metasploit-like parameters.
        scope = ['auxiliary']

def initialise_framework(options):
    pass

@cli.command(help='The main OWTF CLI interface')
@click.option("-proxy", "--proxy", default=True, help="Use this flag to run OWTF Inbound Proxy")
@click.argument("targets", nargs=-1)
def cli(targets):
    app = create_app()
    if proxy:

    scope = targets or []
    num_targets = len(scope)
    if num_targets == 1:  # Check if this is a file
        if os.path.isfile(scope[0]):
            logging.info("Scope file: trying to load targets from it ..")
            new_scope = []
            for target in open(scope[0]).read().split("\n"):
                clean_target = target.strip()
                if not clean_target:
                    continue  # Skip blank lines
                new_scope.append(clean_target)
            if len(new_scope) == 0:  # Bad file
                logging.info("Please provide a scope file (1 target x line)")
            scope = new_scope
    for target in scope:
        if target[0] == "-":
            logging.info("Invalid Target: " + target)

    owtf_pid = os.getpid()
    create_temp_storage_dirs(owtf_pid)

    try:
        _ensure_default_session()
        load_framework_config_file(DEFAULT_FRAMEWORK_CONFIG, FALLBACK_FRAMEWORK_CONFIG, ROOT_DIR, owtf_pid)
        load_config_db_file(DEFAULT_GENERAL_PROFILE, FALLBACK_GENERAL_PROFILE)
        load_resources_from_file(DEFAULT_RESOURCES_PROFILE, FALLBACK_RESOURCES_PROFILE)
        load_mappings_from_file(DEFAULT_MAPPING_PROFILE, FALLBACK_MAPPING_PROFILE)
        load_test_groups(WEB_TEST_GROUPS, FALLBACK_WEB_TEST_GROUPS, "web")
        load_test_groups(NET_TEST_GROUPS, FALLBACK_NET_TEST_GROUPS, "net")
        load_test_groups(AUX_TEST_GROUPS, FALLBACK_AUX_TEST_GROUPS, "aux")
        # After loading the test groups then load the plugins, because of many-to-one relationship
        load_plugins()
    except exceptions.DatabaseNotRunningException:
        sys.exit(-1)

    options = {
        'PluginGroup': None,
        'OnlyPlugins': None
    }
    try:
        logging.info("Loading framework please wait..")
        target_urls = load_targets(scope)
        load_works(target_urls, options)
        start_proxy()
        return True
    except:
        sys.exit(0)  # Not Interrupted or Crashed.
    finally:  # Needed to rename the temp storage dirs to avoid confusion.
        clean_temp_storage_dirs(owtf_pid)
