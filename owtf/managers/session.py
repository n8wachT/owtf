"""
owtf.managers.session
~~~~~~~~~~~~~~~~~~~~~

Manager functions for sessions
"""
from owtf.models.base.session import get_scoped_session
from owtf.lib import exceptions
from owtf.models.session import Session
from owtf.models.target import Target
from owtf.utils.strings import str2bool


def session_required(func):
    """
    In order to use this decorator on a `method` there is one requirements
    , target_id must be a kwarg of the function

    All this decorator does is check if a valid value is passed for target_id
    if not get the target_id from target manager and pass it
    """

    def wrapped_function(*args, **kwargs):
        # True if target_id doesnt exist
        if (kwargs.get("session_id", "None") == "None") or (kwargs.get("session_id", True) is None):
            kwargs["session_id"] = get_session_id(get_scoped_session())
        return func(*args, **kwargs)

    return wrapped_function


def _ensure_default_session(session):
    """If there are no sessions, it will be deadly, so if number of sessions is zero then add a default session

    :return: None
    :rtype: None
    """
    if session.query(Session).count() == 0:
        add_session(session, "default session")


def set_session(session, session_id):
    """Sets the session based on the session id

    :param session_id: Session id
    :type session_id: `int`
    :return: None
    :rtype: None
    """
    query = session.query(Session)
    session_obj = query.get(session_id)
    if session_obj is None:
        raise exceptions.InvalidSessionReference("No session with session_id: {}".format(str(session_id)))
    query.update({'active': False})
    session_obj.active = True
    session.commit()


def get_session_id(session):
    """Gets the active session's id

    :return: ID of the active session
    :rtype: `int`
    """
    session_id = session.query(Session.id).filter_by(active=True).first()
    return session_id


def add_session(session, session_name):
    """Adds a new session to the DB

    :param session_name: Name of the new session
    :type session_name: `str`
    :return: None
    :rtype: None
    """
    existing_obj = session.query(Session).filter_by(name=session_name).first()
    if existing_obj is None:
        session_obj = Session(name=session_name[:50])
        session.add(session_obj)
        session.commit()
        set_session(session, session_obj.id)
    else:
        raise exceptions.DBIntegrityException("Session already exists with session name: {}".format(session_name))


@session_required
def add_target_to_session(session, target_id, session_id=None):
    """Adds the target to the session

    :param target_id: ID of the target to add
    :type target_id: `int`
    :param session_id: ID of the session
    :type session_id: `int`
    :return: None
    :rtype: None
    """
    session_obj = session.query(Session).get(session_id)
    target_obj = session.query(Target).get(target_id)
    if session_obj is None:
        raise exceptions.InvalidSessionReference("No session with id: {}".format(str(session_id)))
    if target_obj is None:
        raise exceptions.InvalidTargetReference("No target with id: {}".format(str(target_id)))
    if session_obj not in target_obj.sessions:
        session_obj.targets.append(target_obj)
    session.commit()


@session_required
def remove_target_from_session(session, target_id, session_id=None):
    """Remove target from a session

    :param target_id: ID of the target
    :type target_id: `int`
    :param session_id: ID of the session
    :type session_id: `int`
    :return: None
    :rtype: None
    """
    session_obj = session.query(Session).get(session_id)
    target_obj = session.query(Target).get(target_id)
    if session_obj is None:
        raise exceptions.InvalidSessionReference("No session with id: {}".format(str(session_id)))
    if target_obj is None:
        raise exceptions.InvalidTargetReference("No target with id: {}".format(str(target_id)))
    session_obj.targets.remove(target_obj)
    # Delete target whole together if present in this session alone
    if len(target_obj.sessions) == 0:
        from owtf.managers.target import delete_target
        delete_target(session, id=target_obj.id)
    session.commit()


def delete_session(session, session_id):
    """Deletes a session from the DB

    :param session_id: ID of the session to delete
    :type session_id: `int`
    :return: None
    :rtype: None
    """
    session_obj = session.query(Session).get(session_id)
    if session_obj is None:
        raise exceptions.InvalidSessionReference("No session with id: {}".format(str(session_id)))
    for target in session_obj.targets:
        # Means attached to only this session obj
        if len(target.sessions) == 1:
            from owtf.managers.target import delete_target
            delete_target(session, id=target.id)
    session.delete(session_obj)
    _ensure_default_session(session)  # i.e if there are no sessions, add one
    session.commit()


def derive_session_dict(session_obj):
    """Fetch the session dict from session obj

    :param session_obj: Session object
    :type session_obj:
    :return: Session dict
    :rtype: `dict`
    """
    sdict = dict(session_obj.__dict__)
    sdict.pop("_sa_instance_state")
    return sdict


def derive_session_dicts(session_objs):
    """Fetch the session dicts from list of session objects

    :param session_obj: List of session objects
    :type session_obj: `list`
    :return: List of session dicts
    :rtype: `list`
    """
    results = []
    for session_obj in session_objs:
        if session_obj:
            results.append(derive_session_dict(session_obj))
    return results


def session_generate_query(session, filter_data=None):
    """Generate query based on filter data

    :param filter_data: Filter data
    :type filter_data: `dict`
    :return:
    :rtype:
    """
    if filter_data is None:
        filter_data = {}
    query = session.query(Session)
    # it doesn't make sense to search in a boolean column :P
    if filter_data.get('active', None):
        if isinstance(filter_data.get('active'), list):
            filter_data['active'] = filter_data['active'][0]
        query = query.filter_by(active=str2bool(filter_data['active']))
    return query.order_by(Session.id)


def get_all_session_dicts(session, filter_data):
    """Get session dicts based on filter criteria

    :param filter_data: Filter data
    :type filter_data: `dict`
    :return: List of session dicts
    :rtype: `dict`
    """
    session_objs = session_generate_query(session, filter_data).all()
    return derive_session_dicts(session_objs)


def get_session_dict(session, session_id):
    """Get the session dict based on the ID

    :param session_id: ID of the session
    :type session_id: `int`
    :return: Session dict
    :rtype: `dict`
    """
    session_obj = session.query(Session).get(session_id)
    if session_obj is None:
        raise exceptions.InvalidSessionReference("No session with id: {}".format(str(session_id)))
    return derive_session_dict(session_obj)
