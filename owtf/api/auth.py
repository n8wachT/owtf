from __future__ import absolute_import, print_function

from functools import wraps
import re
from datetime import datetime
try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin

from flask import current_app, g, request, session
from itsdangerous import BadSignature, JSONWebSignatureSerializer

from owtf.utils import timezone
from owtf.lib.exceptions import AuthenticationFailed
from owtf.models import User


def requires_auth(method):
    """
    Require an authenticated user on given method.
    Return a 401 Unauthorized status on failure.
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


class ApiTokenAuthentication(object):
    def authenticate(self):
        return get_user_from_token()


class SessionAuthentication(object):
    def authenticate(self):
        user = get_current_user()
        if not user:
            return None
        return user


def get_user_from_token():
    header = request.headers.get('Authorization', '').lower()
    if not header:
        return None

    if not header.startswith('bearer'):
        return None

    token = re.sub(r"^bearer(:|\s)\s*", '', header).strip()
    parts = token.split('-', 2)
    if not len(parts) == 3:
        raise AuthenticationFailed

    #TODO
    raise AuthenticationFailed


def get_user_from_request():
    expire = session.get('expire')
    if not expire:
        return None

    try:
        expire = datetime.utcfromtimestamp(expire).replace(tzinfo=timezone.utc)
    except Exception:
        current_app.logger.exception('invalid session expirey')
        del session['expire']
        return None

    if expire <= timezone.now():
        current_app.logger.info('session expired')
        del session['expire']
        return None

    try:
        uid = session['uid']
    except KeyError:
        current_app.logger.error('missing uid session key', exc_info=True)
        del session['expire']
        return None

    return User.query.get(uid)


def login_user(user_id, session=session, current_datetime=None):
    session['uid'] = str(user_id)
    session['expire'] = int((
        (current_datetime or timezone.now()) + current_app.config['PERMANENT_SESSION_LIFETIME']).strftime('%s'))
    session.permanent = True


def logout():
    session.clear()
    g.current_user = None


def get_current_user():
    rv = getattr(g, 'current_user', None)
    if not rv:
        rv = get_user_from_request()
        g.current_user = rv
    return rv


def set_current_user(user):
    current_app.logger.info('Binding user as %r', user)
    g.current_user = user


def get_current_tenant():
    rv = getattr(g, 'current_user', None)
    if rv is None:
        rv = get_user_from_request()
        set_current_user(rv)
    return rv


def generate_token(user):
    s = JSONWebSignatureSerializer(current_app.secret_key, salt='auth')
    payload = {
        'repo_ids': [str(o) for o in user.repository_ids],
    }
    if getattr(user, 'user_id', None):
        payload['uid'] = str(user.user_id)
    return s.dumps(payload)


def parse_token(token):
    s = JSONWebSignatureSerializer(current_app.secret_key, salt='auth')
    try:
        return s.loads(token)
    except BadSignature:
        return None


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        # same scheme
        test_url.scheme in ('http', 'https') and
        # same host and port
        ref_url.netloc == test_url.netloc and
        # and different endoint
        ref_url.path != test_url.path
    )


def get_redirect_target(clear=True):
    if clear:
        session_target = session.pop('next', None)
    else:
        session_target = session.get('next')

    for target in request.values.get('next'), session_target:
        if not target:
            continue
        if is_safe_url(target):
            return target


def bind_redirect_target(target=None):
    if not target:
        target = request.values.get('next') or request.referrer
    if target and is_safe_url(target):
        session['next'] = target
    else:
        session.pop('next', None)
