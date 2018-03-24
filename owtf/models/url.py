"""
owtf.models.url
~~~~~~~~~~~~~~~


"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from owtf.models.base.model_base import Model


class Url(Model):
    __tablename__ = "urls"

    target_id = Column(Integer, ForeignKey("targets.id"))
    url = Column(String, primary_key=True)
    visited = Column(Boolean, default=False)
    scope = Column(Boolean, default=True)

    def __repr__(self):
        return "<URL (url='%s')>" % (self.url)
