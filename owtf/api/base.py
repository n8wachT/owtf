import json
from functools import wraps
import logging

from flask import Response, request
from flask_restful import Resource

from owtf.config import db


def _as_json(context):
    try:
        return json.dumps(context)
    except TypeError:
        logging.warning("unable to json-encode api response. Was the data not serialized?")


def error(message, problems=None, http_code=400):
    """ Returns a new error response to send API clients.
    :param message: A human readable description of the error
    :param problems: List of fields that caused the error.
    :param http_code: The HTTP code to use for the response.
    """
    error_response = {'error': message}
    if problems:
        error_response['problems'] = problems
    return error_response, http_code


def param(key, validator=lambda x: x, required=True, dest=None):
    def wrapped(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            if key in kwargs:
                value = kwargs.pop(key, '')
            elif request.method == 'POST':
                value = request.form.get(key) or ''
            else:
                value = ''

            dest_key = str(dest or key)

            value = value.strip()
            if not value:
                if required:
                    raise ParamError(key, 'value is required')
                return func(*args, **kwargs)

            try:
                value = validator(value)
            except ParamError:
                raise
            except Exception:
                raise ParamError(key, 'invalid value')

            kwargs[dest_key] = value

            return func(*args, **kwargs)

        return _wrapped
    return wrapped


class APIError(Exception):
    pass


class ParamError(APIError):

    def __init__(self, key, msg):
        self.key = key
        self.msg = msg

    def __unicode__(self):
        return '{0} is not valid: {1}'.format(self.key, self.msg)


class APIView(Resource):
    def dispatch_request(self, *args, **kwargs):
        try:
            response = super(APIView, self).dispatch_request(*args, **kwargs)
        except Exception:
            db.session.rollback()
            raise
        else:
            db.session.commit()
        return response

    def respond(self, context, status_code=200):
        data = context
        response = Response(
            _as_json(data),
            mimetype='application/json',
            status=status_code,
        )
        return response
