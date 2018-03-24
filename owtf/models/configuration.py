"""

"""
from sqlalchemy import Column, String, Boolean

from owtf.models.base.model_base import Model


class Configuration(Model):
    __tablename__ = "configuration"

    key = Column(String, primary_key=True)
    value = Column(String)
    section = Column(String)
    descrip = Column(String, nullable=True)
    dirty = Column(Boolean, default=False)

    def __repr__(self):
        return "<ConfigItem (key='%s', value='%s', dirty='%r')>" % (self.key, self.value, self.dirty)
