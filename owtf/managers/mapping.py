"""
owtf.managers.mapping
~~~~~~~~~~~~~~~~~~~~~

Manages the mapping between different plugin groups and codes
"""
import json

from owtf.lib.exceptions import InvalidMappingReference
from owtf.managers.config import load_config_file
from owtf.models.mapping import Mapping
from owtf.utils.pycompat import iteritems

mapping_types = []


def get_mapping_types():
    """In memory data saved when loading db
    :return: None
    :rtype: None
    """
    return mapping_types


def derive_mapping_dict(obj):
    """Fetch the mapping dict from an object

    :param obj: The mapping object
    :type obj:
    :return: Mappings dict
    :rtype: `dict`
    """
    if obj:
        pdict = dict(obj.__dict__)
        pdict.pop("_sa_instance_state", None)
        # If output is present, json decode it
        if pdict.get("mappings", None):
            pdict["mappings"] = json.loads(pdict["mappings"])
        return pdict


def derive_mapping_dicts(obj_list):
    """Fetches the mapping dicts based on the objects list

    :param obj_list: The plugin object list
    :type obj_list: `list`
    :return: Mapping dicts as a list
    :rtype: `list`
    """
    dict_list = []
    for obj in obj_list:
        dict_list.append(derive_mapping_dict(obj))
    return dict_list


def get_all_mappings(session):
    """Create a mapping between OWTF plugins code and OWTF plugins description.

    :return: Mapping dictionary {code: [mapped_code, mapped_description], code2: [mapped_code, mapped_description], ...}
    :rtype: dict
    """


def get_mappings(session, mapping_type):
    """Fetches mappings from DB based on mapping type

    :param mapping_type: Mapping type like OWTF, OWASP (v3, v4, Top 10), NIST, CWE
    :type mapping_type: `str`
    :return: Mappings
    :rtype: `dict`
    """
    if mapping_type in mapping_types:
        mapping_objs = session.query(Mapping).all()
        mappings = {}
        for mapping_dict in derive_mapping_dicts(mapping_objs):
            if mapping_dict["mappings"].get(mapping_type, None):
                mappings[mapping_dict["owtf_code"]] = mapping_dict["mappings"][mapping_type]
        return mappings
    else:
        raise InvalidMappingReference("InvalidMappingReference %s requested" % mapping_type)


def get_mapping_category(session, plugin_code):
    """Get the categories for a plugin code

    :param plugin_code: The code for the specific plugin
    :type plugin_code:  `int`
    :return: category for the plugin code
    :rtype: `str`
    """
    category = session.query(Mapping.category).get(plugin_code)
    # Getting the corresponding category back from db
    return category


def load_mappings(session, default, fallback):
    """Loads the mappings from the config file

    .note::
        This needs to be a list instead of a dictionary to preserve order in python < 2.7

    :param session: SQLAlchemy database session
    :type session: `object`
    :param default: The fallback path to config file
    :type default: `str`
    :param fallback: The path to config file
    :type fallback: `str`
    :return: None
    :rtype: None
    """
    config_dump = load_config_file(default, fallback)
    for owtf_code, mappings in iteritems(config_dump):
        category = None
        if 'category' in mappings:
            category = mappings.pop('category')
        session.merge(Mapping(owtf_code=owtf_code, mappings=json.dumps(mappings), category=category))
    session.commit()
