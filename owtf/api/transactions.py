"""
owtf.api.handlers.transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from flask import request
from werkzeug.exceptions import BadRequest

from owtf.api.base import APIView
from owtf.lib import exceptions
from owtf.lib.exceptions import InvalidTargetReference, InvalidParameterType, InvalidTransactionReference
from owtf.managers.transaction import get_by_id_as_dict, get_all_transactions_dicts, delete_transaction, \
    get_hrt_response, search_all_transactions
from owtf.managers.url import get_all_urls, search_all_urls


class TransactionData(APIView):
    methods = ['GET', 'DELETE']

    def get(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                self.respond(get_by_id_as_dict(int(transaction_id), target_id=int(target_id)))
            else:
                # Empty criteria ensure all transactions
                filter_data = request.view_args
                self.respond(get_all_transactions_dicts(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidTransactionReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()

    def post(self, target_url):
        raise BadRequest()

    def put(self):
        raise BadRequest()

    def patch(self):
        raise BadRequest()

    def delete(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                delete_transaction(int(transaction_id), int(target_id))
            else:
                raise BadRequest()
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()


class TransactionHrt(APIView):
    methods = ['POST']

    def post(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                filter_data = request.view_args
                self.respond(get_hrt_response(filter_data, int(transaction_id), target_id=int(target_id)))
            else:
                raise BadRequest()
        except (InvalidTargetReference, InvalidTransactionReference, InvalidParameterType) as e:
            logging.warn(e.parameter)
            raise BadRequest()


class TransactionSearch(APIView):
    methods = ['GET']

    def get(self, target_id=None):
        if not target_id:  # Must be a integer target id
            raise BadRequest()
        try:
            # Empty criteria ensure all transactions
            filter_data = request.view_args
            filter_data["search"] = True
            self.respond(search_all_transactions(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidTransactionReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()


class URLData(APIView):
    methods = ['GET']

    def get(self, target_id=None):
        try:
            # Empty criteria ensure all transactions
            filter_data = request.view_args
            self.respond(get_all_urls(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()


class URLSearch(APIView):
    methods = ['GET']

    def get(self, target_id=None):
        if not target_id:  # Must be a integer target id
            raise BadRequest()
        try:
            # Empty criteria ensure all transactions
            filter_data = request.view_args
            filter_data["search"] = True
            self.respond(search_all_urls(filter_data, target_id=int(target_id)))
        except exceptions.InvalidTargetReference as e:
            logging.warn(e.parameter)
            raise BadRequest()
        except exceptions.InvalidParameterType as e:
            logging.warn(e.parameter)
            raise BadRequest()
