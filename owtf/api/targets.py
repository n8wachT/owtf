"""
owtf.api.handlers.targets
~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from flask import request
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.lib.exceptions import InvalidTargetReference
from owtf.managers.target import get_target_config_by_id, get_target_config_dicts, add_targets, update_target, \
    delete_target, search_target_configs


class TargetConfig(APIView):
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def get(self, target_id=None):
        try:
            # If no target_id, means /target is accessed with or without filters
            if not target_id:
                # Get all filter data here, so that it can be passed
                filter_data = dict(request.view_args)
                self.respond(get_target_config_dicts(filter_data))
            else:
                self.respond(get_target_config_by_id(target_id))
        except InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def post(self, target_id=None):
        if (target_id) or (not request.view_args.get("target_url", default=None)):  # How can one post using an id xD
            raise BadRequest()
        try:
            add_targets(request.view_args.get("target_url"))
            return "{}", 201  # Stands for "201 Created"
        except exceptions.DBIntegrityException as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.UnresolvableTargetException as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def put(self, target_id=None):
        return self.patch(target_id)

    def patch(self, target_id=None):
        if not target_id or not request.view_args:
            raise BadRequest()
        try:
            patch_data = request.view_args
            update_target(patch_data, id=target_id)
        except InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def delete(self, target_id=None):
        if not target_id:
            raise BadRequest()
        try:
            delete_target(id=target_id)
        except InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()


class TargetConfigSearch(APIView):
    methods = ['GET']

    def get(self):
        try:
            filter_data = request.view_args
            filter_data["search"] = True
            self.respond(search_target_configs(filter_data=filter_data))
        except exceptions.InvalidParameterType:
            raise BadRequest()
