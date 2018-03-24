"""
owtf.models.work
~~~~~~~~~~~~~~~~


"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint

from owtf.models.base.model_base import Model


class Work(Model):
    __tablename__ = "worklist"
    __table_args__ = (UniqueConstraint('target_id', 'plugin_key'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    active = Column(Boolean, default=True)

    # Columns plugin and target are created using backrefs

    def __repr__(self):
        return "<Work (target='%s', plugin='%s')>" % (self.target_id, self.plugin_key)
