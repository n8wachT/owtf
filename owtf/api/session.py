"""
owtf.api.handlers.session
~~~~~~~~~~~~~~~~~~~~~~

"""

from flask import request, Response
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.managers.session import get_all_session_dicts, get_session_dict, add_session, add_target_to_session, \
    remove_target_from_session, set_session, delete_session


class OWTFSession(APIView):
    SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def get(self, session_id=None, action=None):
        if action is not None:  # Action must be there only for put
            raise BadRequest()
        if session_id is None:
            filter_data = request.view_args
            self.respond(get_all_session_dicts(filter_data))
        else:
            try:
                self.respond(get_session_dict(session_id))
            except exceptions.InvalidSessionReference:
                raise BadRequest()

    def post(self, session_id=None, action=None):
        if (session_id is not None) or (request.view_args.get("name", None) is None) or (action is not None):
            # Not supposed to post on specific session
            raise BadRequest()
        try:
            add_session(request.view_args.get("name"))
            return Response("{}", status=201, mimetype='application/json')  # Stands for "201 Created"
        except exceptions.DBIntegrityException:
            raise BadRequest()

    def patch(self, session_id=None, action=None):
        target_id = request.view_args.get("target_id", None)
        if (session_id is None) or (target_id is None and action in ["add", "remove"]):
            raise BadRequest()
        try:
            if action == "add":
                add_target_to_session(int(request.view_args.get("target_id")), session_id=int(session_id))
            elif action == "remove":
                remove_target_from_session(int(request.view_args.get("target_id")), session_id=int(session_id))
            elif action == "activate":
                set_session(int(session_id))
        except exceptions.InvalidTargetReference:
            raise BadRequest()
        except exceptions.InvalidSessionReference:
            raise BadRequest()

    def delete(self, session_id=None, action=None):
        if (session_id is None) or action is not None:
            raise BadRequest()
        try:
            delete_session(int(session_id))
        except exceptions.InvalidSessionReference:
            raise BadRequest()
