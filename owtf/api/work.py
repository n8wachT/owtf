"""
owtf.api.handlers.work
~~~~~~~~~~~~~

"""

import logging

from flask import request
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.managers.plugin import get_all_plugin_dicts
from owtf.managers.target import get_target_config_dicts
from owtf.work.worker import worker_manager
from owtf.work.worklist import get_all_work, get_work, add_work, remove_work, delete_all_work, patch_work, \
    pause_all_work, resume_all_work, search_all_work
from owtf.utils.strings import str2bool


class Worker(APIView):
    methods = ['GET', 'POST', 'DELETE', 'OPTIONS']

    def set_default_headers(self):
        request.headers["Access-Control-Allow-Origin"] = "*"
        request.headers["Access-Control-Allow-Methods"] =  "GET, POST, DELETE"

    def get(self, worker_id=None, action=None):
        if not worker_id:
            self.respond(worker_manager.get_worker_details())
        try:
            if worker_id and (not action):
                self.respond(worker_manager.get_worker_details(int(worker_id)))
            if worker_id and action:
                if int(worker_id) == 0:
                    getattr(worker_manager, '%s_all_workers' % action)()
                getattr(worker_manager, '%s_worker' % action)(int(worker_id))
        except exceptions.InvalidWorkerReference as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def post(self, worker_id=None, action=None):
        if worker_id or action:
            raise BadRequest()
        worker_manager.create_worker()
        return "{}", 201  # Stands for "201 Created"

    def options(self, worker_id=None, action=None):
        return "{}", 200

    def delete(self, worker_id=None, action=None):
        if (not worker_id) or action:
            raise BadRequest()
        try:
            worker_manager.delete_worker(int(worker_id))
        except exceptions.InvalidWorkerReference as e:
            logging.warn(e.parameter)
            raise BadRequest()


class Worklist(APIView):
    methods = ['GET', 'POST', 'DELETE', 'PATCH']

    def get(self, work_id=None, action=None):
        try:
            if work_id is None:
                criteria = request.view_args
                self.respond(get_all_work(criteria))
            else:
                self.respond(get_work((work_id)))
        except exceptions.InvalidParameterType:
            raise BadRequest()
        except exceptions.InvalidWorkReference:
            raise BadRequest()

    def post(self, work_id=None, action=None):
        if work_id is not None or action is not None:
            BadRequest()
        try:
            filter_data = request.view_args
            if not filter_data:
                raise BadRequest()
            plugin_list = get_all_plugin_dicts(filter_data)
            target_list = get_target_config_dicts(filter_data)
            if (not plugin_list) or (not target_list):
                raise BadRequest()
            force_overwrite = str2bool(request.view_args.get("force_overwrite", "False"))
            add_work(target_list, plugin_list, force_overwrite=force_overwrite)
            return "{}", 201
        except exceptions.InvalidTargetReference:
            raise BadRequest()
        except exceptions.InvalidParameterType:
            raise BadRequest()

    def delete(self, work_id=None, action=None):
        if work_id is None or action is not None:
            BadRequest()
        try:
            work_id = int(work_id)
            if work_id != 0:
                remove_work(work_id)
                return "{}", 200
            else:
                if action == 'delete':
                    delete_all_work()
        except exceptions.InvalidTargetReference:
            raise BadRequest()
        except exceptions.InvalidParameterType:
            raise BadRequest()
        except exceptions.InvalidWorkReference:
            raise BadRequest()

    def patch(self, work_id=None, action=None):
        if work_id is None or action is None:
            BadRequest()
        try:
            work_id = int(work_id)
            if work_id != 0:  # 0 is like broadcast address
                if action == 'resume':
                    patch_work(work_id, active=True)
                elif action == 'pause':
                    patch_work(work_id, active=False)
            else:
                if action == 'pause':
                    pause_all_work()
                elif action == 'resume':
                    resume_all_work()
        except exceptions.InvalidWorkReference:
            raise BadRequest()


class WorklistSearch(APIView):
    methods = ['GET']

    def get(self):
        try:
            criteria = request.view_args
            criteria["search"] = True
            self.respond(search_all_work(criteria))
        except exceptions.InvalidParameterType:
            raise BadRequest()
