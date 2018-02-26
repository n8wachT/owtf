"""
owtf.db.db
~~~~~~~~~~

This file handles all the database transactions.
"""
import binascii
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from owtf.config import db
from owtf.utils import timezone


def try_create(model, where, defaults=None):
    if defaults is None:
        defaults = {}

    instance = model()
    for key, value in defaults.items():
        setattr(instance, key, value)
    for key, value in where.items():
        setattr(instance, key, value)
    try:
        with db.session.begin_nested():
            db.session.add(instance)
    except IntegrityError:
        return
    return instance


def try_update(model, where, values):
    result = db.session.query(type(model)).filter_by(**where).update(
        values, synchronize_session=False
    )
    return result.rowcount > 0


def get_or_create(model, where, defaults=None):
    if defaults is None:
        defaults = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is not None:
        return instance, created

    instance = try_create(model, where, defaults)
    if instance is None:
        instance = model.query.filter_by(**where).first()
    else:
        created = True

    if instance is None:
        # this should never happen unless everything is broken
        raise Exception('Unable to get or create instance')

    return instance, created


def create_or_update(model, where, values=None):
    if values is None:
        values = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is None:
        instance = try_create(model, where, values)
        if instance is None:
            instance = model.query.filter_by(**where).first()
            if instance is None:
                raise Exception('Unable to create or update instance')
            update(instance, values)
        else:
            created = True
    else:
        update(instance, values)

    return instance, created


def create_or_get(model, where, values=None):
    if values is None:
        values = {}

    created = False

    instance = model.query.filter_by(**where).first()
    if instance is None:
        instance = try_create(model, where, values)
        if instance is None:
            instance = model.query.filter_by(**where).first()
        else:
            created = True

        if instance is None:
            raise Exception('Unable to get or create instance')

    return instance, created


def update(instance, values):
    for key, value in values.items():
        if getattr(instance, key) != value:
            setattr(instance, key, value)
    db.session.add(instance)


def model_repr(*attrs):
    if 'id' not in attrs:
        attrs = ('id', ) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = ('%s=%s' % (a, repr(getattr(self, a, None))) for a in attrs)

        return u'<%s at 0x%x: %s>' % (cls, id(self), ', '.join(pairs))

    return _repr


class StandardAttributes(object):
    @declared_attr
    def date_created(cls):
        return db.Column(
            db.TIMESTAMP(timezone=True),
            default=timezone.now,
            server_default=func.now(),
            nullable=False
        )


class ApiTokenMixin(object):
    @declared_attr
    def key(cls):
        return db.Column(
            db.String(64), default=lambda: ApiTokenMixin.generate_token(), unique=True, nullable=False
        )

    @classmethod
    def generate_token(cls):
        return binascii.hexlify(os.urandom(32))

    def get_token_key(self):
        raise NotImplementedError

    def get_tenant(self):
        raise NotImplementedError
