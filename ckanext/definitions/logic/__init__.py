from ckan import model
from ckan.lib.search import index_for
from ckan.plugins import toolkit
import logging
from ckanext.definitions.model import Definition

log = logging.getLogger(__name__)

PACKAGE_INDEX = index_for(model.Package)


def reindex_package(package_id, defer_commit=False):
    context = {'model': model, 'ignore_auth': True, 'validate': False, 'use_cache': False}
    pkg_dict = toolkit.get_action('package_show')(context, {'id': package_id})
    PACKAGE_INDEX.update_dict(pkg_dict, defer_commit=defer_commit)
    return pkg_dict


def reindex_packages(package_ids, defer_commit=False):
    pkg_dicts = [reindex_package(package_id, True) for package_id in package_ids]
    if not defer_commit:
        PACKAGE_INDEX.commit()
    return pkg_dicts


def get_definition_object(context, data_dict, key='id'):
    name = "definition"
    if not data_dict:
        data_dict = {}
    id = data_dict.get(key, None)
    if name in context:
        return context[name]
    else:
        if not id:
            raise toolkit.ValidationError('Missing id, can not get Definition object')
        obj = Definition.get(id)
        if not obj:
            raise toolkit.ObjectNotFound
        # Save in case we need this again during the request
        context[name] = obj
        return obj
