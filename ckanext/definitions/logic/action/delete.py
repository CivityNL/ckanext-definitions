# encoding: utf-8

'''API functions for deleting data from CKAN.'''
import logging
from ckan.plugins import toolkit
from ckanext.definitions.model import Definition
from ckanext.definitions.logic.action import reindex_package, reindex_packages, \
    create_definition_package_relationship_activities
from ckan.model import Activity

log = logging.getLogger(__name__)


def definition_delete(context, data_dict):
    '''Delete a definition.

    You must be a Data Officer to delete definitions.
    Also deletes all Package_definitions from the packages associated

    :param id: the id of the definition
    :type id: string

    '''

    model = context['model']
    definition_id = toolkit.get_or_bust(data_dict, 'id')

    toolkit.check_access('definition_delete', context, data_dict)

    # check if definition exists
    definition_obj = Definition.get(definition_id)
    if definition_obj is None:
        raise toolkit.ObjectNotFound(toolkit._('Could not find definition "%s"') % definition_id)

    existing_packages = definition_obj.packages_all

    # Delete the actual Definition
    definition_obj.delete()
    model.repo.commit()

    reindex_packages([package.id for package in existing_packages])

    return {'success': True,
            'msg': 'successfully deleted definition {0}'.format(definition_id)}


def definition_data_officer_delete(context, data_dict):
    '''
    Removes the role Data Officer from a User
    :param context:
    :param data_dict: contains 'user_id'
    :return: the definition added to the DB
    '''

    # check for valid input
    user_id = toolkit.get_or_bust(data_dict, 'user_id')

    user_dict = toolkit.get_action("user_show")(context, {"id": user_id, "include_plugin_extras": True})

    user_plugin_extras = user_dict.get('plugin_extras', {}) or {}
    definition_plugin_extras = user_plugin_extras.get('definition', {})

    if 'data_officer' in definition_plugin_extras and not definition_plugin_extras.get('data_officer'):
        raise toolkit.NotFound('Data Officer "{id}" was not found.'.format(id=user_id))
    else:
        definition_plugin_extras['data_officer'] = False
        user_plugin_extras['definition'] = definition_plugin_extras
        toolkit.get_action('user_patch')(dict(context, ignore_auth=True), {"id": user_id, 'plugin_extras': user_plugin_extras})


def definition_package_relationship_delete(context, data_dict):
    '''
    Removes the role Definitions from the dataset
    :param context:
    :param data_dict: contains 'package_id' and 'definition_id'
    :return: True if Successfull, otherwise False
    '''

    # check for valid input
    model = context['model']
    session = context['session']
    user = context['user']

    package_id, definition_id = toolkit.get_or_bust(data_dict, ['package_id', 'definition_id'])

    # check if package exists
    package = model.Package.get(package_id)
    if package is None:
        raise toolkit.ObjectNotFound(toolkit._('Package not found'))
    definition = Definition.get(definition_id)
    if definition is None:
        raise toolkit.ObjectNotFound(toolkit._('Definition not found'))

    if not package.id in [p.id for p in definition.packages_all]:
        raise toolkit.ValidationError(toolkit._("Package {} is not linked to definition {}".format(
            package.id, definition.id
        )))

    definition.packages_all.remove(package)
    session.add(definition)
    session.flush()
    create_definition_package_relationship_activities(session, definition, package, user, "removed")
    session.commit()
    pkg_dict = reindex_package(package.id)

    return pkg_dict
