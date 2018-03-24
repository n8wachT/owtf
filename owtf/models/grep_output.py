"""
owtf.models.grep_output
~~~~~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint

from owtf.models.base.model_base import Model


class GrepOutput(Model):
    __tablename__ = "grep_outputs"
    __table_args__ = (UniqueConstraint('name', 'output', 'target_id'),)

    # Also has a column transactions, which is added by
    # using backref in transaction
    target_id = Column(Integer, ForeignKey("targets.id"))
    id = Column(Integer, primary_key=True)
    name = Column(String)
    output = Column(Text)
