from __future__ import absolute_import, print_function

from functools import wraps

NOT_SET = object()


def requires_auth(method):
    """
    Require an authenticated user on given method.
    Return a 401 Unauthorized status on failure.
    >>> @requires_admin
    >>> def post(self):
    >>>     # ...
    """
    @wraps(method)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return '', 401
        return method(*args, **kwargs)
    return wrapped


class ResourceNotFound(Exception):
    pass
