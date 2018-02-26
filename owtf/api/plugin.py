"""
owtf.api.plugin
~~~~~~~~~~~~~~~

"""

import collections
import logging

from flask import request
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.managers.mapping import get_all_mappings
from owtf.managers.plugin import get_types_for_plugin_group, get_all_plugin_dicts, get_all_test_groups
from owtf.managers.poutput import get_all_poutputs, update_poutput, delete_all_poutput


class PluginData(APIView):
    SUPPORTED_METHODS = ['GET']

    def get(self, plugin_group=None, plugin_type=None, plugin_code=None):
        try:
            filter_data = dict(request.view_args)
            if not plugin_group:  # Check if plugin_group is present in url
                self.respond(get_all_plugin_dicts(filter_data))
            if plugin_group and (not plugin_type) and (not plugin_code):
                filter_data.update({"group": plugin_group})
                self.respond(get_all_plugin_dicts(filter_data))
            if plugin_group and plugin_type and (not plugin_code):
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({"type": plugin_type, "group": plugin_group})
                self.respond(get_all_plugin_dicts(filter_data))
            if plugin_group and plugin_type and plugin_code:
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({"type": plugin_type, "group": plugin_group, "code": plugin_code})
                # This combination will be unique, so have to return a dict
                results = get_all_plugin_dicts(filter_data)
                if results:
                    self.respond(results[0])
                else:
                    raise BadRequest()
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()


class PluginNameOutput(APIView):
    SUPPORTED_METHODS = ['GET']

    def get(self, target_id=None):
        """Retrieve scan results for a target.
        :return: {code: {data: [], details: {}}, code2: {data: [], details: {}} }
        This API doesn't return `output` section as part of optimization.
        `data` is array of scan results according to `plugin_types`.
        `details` contains info about `code`.
        """
        try:
            filter_data = dict(request.view_args)
            results = get_all_poutputs(filter_data, target_id=int(target_id), inc_output=False)

            # Get mappings
            mappings = get_all_mappings()

            # Get test groups as well, for names and info links
            groups = {}
            for group in get_all_test_groups():
                group['mappings'] = mappings.get(group['code'], {})
                groups[group['code']] = group

            dict_to_return = collections.OrderedDict()
            for item in results:
                if (dict_to_return.has_key(item['plugin_code'])):
                    dict_to_return[item['plugin_code']]['data'].append(item)
                else:
                    ini_list = []
                    ini_list.append(item)
                    dict_to_return[item["plugin_code"]] = {}
                    dict_to_return[item["plugin_code"]]["data"] = ini_list
                    dict_to_return[item["plugin_code"]]["details"] = groups[item["plugin_code"]]
            dict_to_return = sorted(dict_to_return.items())
            if results:
                self.respond(dict_to_return)
            else:
                raise BadRequest()

        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()


class PluginOutput(APIView):
    SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def get(self, target_id=None, plugin_group=None, plugin_type=None, plugin_code=None):
        try:
            filter_data = request.view_args
            if plugin_group and (not plugin_type):
                filter_data.update({"plugin_group": plugin_group})
            if plugin_type and plugin_group and (not plugin_code):
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({"plugin_type": plugin_type, "plugin_group": plugin_group})
            if plugin_type and plugin_group and plugin_code:
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({
                    "plugin_type": plugin_type,
                    "plugin_group": plugin_group,
                    "plugin_code": plugin_code
                })
            results = get_all_poutputs(filter_data, target_id=int(target_id), inc_output=True)
            if results:
                self.respond(results)
            else:
                raise BadRequest()

        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def post(self, target_url):
        raise BadRequest()

    def put(self):
        raise BadRequest()

    def patch(self, target_id=None, plugin_group=None, plugin_type=None, plugin_code=None):
        try:
            if (not target_id) or (not plugin_group) or (not plugin_type) or (not plugin_code):
                raise BadRequest()
            else:
                patch_data = request.view_args
                update_poutput(plugin_group, plugin_type, plugin_code, patch_data, target_id=target_id)
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def delete(self, target_id=None, plugin_group=None, plugin_type=None, plugin_code=None):
        try:
            filter_data = request.view_args
            if not plugin_group:  # First check if plugin_group is present in url
                delete_all_poutput(filter_data, target_id=int(target_id))
            if plugin_group and (not plugin_type):
                filter_data.update({"plugin_group": plugin_group})
                delete_all_poutput(filter_data, target_id=int(target_id))
            if plugin_type and plugin_group and (not plugin_code):
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({"plugin_type": plugin_type, "plugin_group": plugin_group})
                delete_all_poutput(filter_data, target_id=int(target_id))
            if plugin_type and plugin_group and plugin_code:
                if plugin_type not in get_types_for_plugin_group(plugin_group):
                    raise BadRequest()
                filter_data.update({
                    "plugin_type": plugin_type,
                    "plugin_group": plugin_group,
                    "plugin_code": plugin_code
                })
                delete_all_poutput(filter_data, target_id=int(target_id))
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()
