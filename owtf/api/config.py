from flask import request, jsonify
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.managers.config import get_all_config_dicts, update_config_val


class Configuration(APIView):
    SUPPORTED_METHODS = ['GET', 'PATCH']

    def get(self):
        filter_data = request.view_args
        self.respond(get_all_config_dicts(filter_data))

    def patch(self):
        for key, value_list in list(request.view_args.items()):
            try:
                update_config_val(key, value_list[0])
            except exceptions.InvalidConfigurationReference:
                raise BadRequest()
