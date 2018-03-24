"""
owtf.models.mapping
~~~~~~~~~~~~~~~~~~~

"""
from sqlalchemy import Column, String

from owtf.models.base.model_base import Model


class Mapping(Model):
    __tablename__ = 'mappings'

    owtf_code = Column(String, primary_key=True)
    mappings = Column(String)
    category = Column(String, nullable=True)

    def get_all(self, session):
        mapping_objs = session.query(Mapping).all()
        return {mapping['owtf_code']: mapping['mappings'] for mapping in derive_mapping_dicts(mapping_objs)}
