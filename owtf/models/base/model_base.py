"""
owtf.models.base.model_base

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_session

from owtf.utils.sql import ClassProperty


class _Model(object):
    """ Custom model mixin with helper methods. """

    @property
    def session(self):
        return object_session(self)

    @classmethod
    def get(cls, session, **kwargs):
        instance = session.query(cls).filter_by(**kwargs).scalar()
        if instance:
            return instance
        return None

    @classmethod
    def get_or_create(cls, session, **kwargs):
        instance = session.query(cls).filter_by(**kwargs).scalar()
        if instance:
            return instance, False

        instance = cls(**kwargs)
        instance.add(session)

        return instance, True

    def just_created(self):
        pass

    def add(self, session):
        session._add(self)
        self.just_created()
        return self

    def delete(self, session):
        session._delete(self)
        return self

    @ClassProperty
    def query(cls, session):
        """
        :rtype: Query
        """
        return session.query(cls)

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def first(cls):
        return cls.query.first()

    @classmethod
    def find(cls, id_):
        """Find record by the id
        :param id_: the primary key
        """
        return cls.query.get(id_)


Model = declarative_base(cls=_Model)
