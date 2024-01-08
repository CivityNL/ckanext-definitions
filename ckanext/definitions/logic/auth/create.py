import logging
from ckanext.definitions.logic.auth import auth_is_data_officer, definition_data_officer_manage
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    user = context.get('user')
    if not auth_is_data_officer(context):
        msg = toolkit._('User {user} is not authorized to create definitions'.format(user=user))
        return {'success': False, 'msg': msg}
    return {'success': True}


def definition_data_officer_create(context, data_dict):
    return definition_data_officer_manage(context, data_dict)


def definition_package_relationship_create(context, data_dict):
    user = context.get('user')
    package_id = data_dict.get('package_id')
    try:
        toolkit.check_access('package_update', context, {"id": package_id})
    except toolkit.NotAuthorized:
        msg = toolkit._('User {user} is not authorized to add definitions to package {package}'.format(user=user, package=package_id))
        return {"success": False, "msg": msg}
    definition_id = data_dict.get('definition_id')
    try:
        toolkit.check_access('definition_show', context, {"id": definition_id})
    except toolkit.NotAuthorized:
        msg = toolkit._('User {user} is not authorized to add definition {definition} to package {package}'.format(user=user, definition=definition_id, package=package_id))
        return {"success": False, "msg": msg}

    return {"success": True}
