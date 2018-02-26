"""
owtf.lib.exceptions
~~~~~~~~~~~~~~~~~~~

Declares the framework exceptions and HTTP errors
"""

import json
from collections import OrderedDict


class FrameworkException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class FrameworkAbortException(FrameworkException):
    pass


class PluginAbortException(FrameworkException):
    pass


class UnreachableTargetException(FrameworkException):
    pass


class UnresolvableTargetException(FrameworkException):
    pass


class DBIntegrityException(FrameworkException):
    pass


class InvalidTargetReference(FrameworkException):
    pass


class InvalidSessionReference(FrameworkException):
    pass


class InvalidTransactionReference(FrameworkException):
    pass


class InvalidParameterType(FrameworkException):
    pass


class InvalidWorkerReference(FrameworkException):
    pass


class InvalidErrorReference(FrameworkException):
    pass


class InvalidWorkReference(FrameworkException):
    pass


class InvalidConfigurationReference(FrameworkException):
    pass


class InvalidUrlReference(FrameworkException):
    pass


class InvalidActionReference(FrameworkException):
    pass


class InvalidMessageReference(FrameworkException):
    pass


class InvalidMappingReference(FrameworkException):
    pass


class DatabaseNotRunningException(Exception):
    pass


class PluginException(Exception):
    pass


class PluginsDirectoryDoesNotExist(PluginException):
    """The specified plugin directory does not exist."""


class PluginsAlreadyLoaded(PluginException):
    """`load_plugins()` called twice."""


class AuthenticationFailed(Exception):
    pass


class ApiError(Exception):
    code = None
    json = None

    def __init__(self, text=None, code=None):
        if code is not None:
            self.code = code
        self.text = text
        if text:
            try:
                self.json = json.loads(text, object_pairs_hook=OrderedDict)
            except ValueError:
                self.json = None
        else:
            self.json = None
        super(ApiError, self).__init__((text or '')[:128])

    @classmethod
    def from_response(cls, response):
        if response.status_code == 401:
            return ApiUnauthorized(response.text)
        return cls(response.text, response.status_code)


class ApiUnauthorized(ApiError):
    code = 401
