from ckanext.definitions.logic.auth import auth_is_data_officer
from ckan.plugins import toolkit


def definition_update(context, data_dict):
    user = context.get('user')
    if not auth_is_data_officer(context):
        msg = toolkit._('User {user} is not authorized to edit definitions'.format(user=user))
        return {'success': False, 'msg': msg}
    return {'success': True}
