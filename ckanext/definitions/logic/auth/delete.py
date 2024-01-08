from ckanext.definitions.logic.auth import auth_is_data_officer, definition_data_officer_manage
from ckan.plugins import toolkit


def definition_delete(context, data_dict):
    user = context.get('user')
    if not auth_is_data_officer(context):
        msg = toolkit._('User {user} is not authorized to delete definitions'.format(user=user))
        return {'success': False, 'msg': msg}
    return {'success': True}


def definition_data_officer_delete(context, data_dict):
    return definition_data_officer_manage(context, data_dict)


def definition_package_relationship_delete(context, data_dict):
    user = context.get('user')
    package_id = toolkit.get_or_bust(data_dict, 'package_id')
    try:
        toolkit.check_access('package_update', context, {"id": package_id})
    except toolkit.NotAuthorized:
        msg = toolkit._('User {user} is not authorized to remove definitions from package {package}'.format(user=user, package=package_id))
        return {"success": False, "msg": msg}
    return {'success': True}
