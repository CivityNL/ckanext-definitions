import ckan.plugins.toolkit as toolkit
from ckanext.definitions.logic import get_definition_object
from ckanext.definitions.logic.auth import auth_is_data_officer


@toolkit.auth_allow_anonymous_access
def definition_show(context, data_dict):
    user = context.get("user")
    definition = get_definition_object(context, data_dict)
    authorized = definition.enabled or auth_is_data_officer(context)

    if not authorized:
        msg = toolkit._('User {user} is not authorized to read definition {definition}'.format(user=user, definition=definition.id))
        return {'success': False, 'msg': msg}
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def definition_list(context, data_dict):
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def definition_search(context, data_dict):
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def definition_autocomplete(context, data_dict):
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def definition_data_officer_list(context, data_dict):
    print("AUTH :: definition_data_officer_list :: data_dict = {}".format(data_dict))
    user = context.get('user')
    if data_dict is None:
        data_dict = {}
    try:
        toolkit.check_access('user_list', context, data_dict)
    except toolkit.NotAuthorized:
        msg = toolkit._('User {user} is not authorized to see data officers'.format(user=user))
        return {"success": False, "msg": msg}
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def definition_activity_list(context, data_dict):
    user = context.get("user")
    definition = get_definition_object(context, data_dict)
    authorized = definition.enabled or auth_is_data_officer(context)

    if not authorized:
        msg = toolkit._('User {user} is not authorized to read definition {definition}'.format(user=user, definition=definition.id))
        return {'success': False, 'msg': msg}
    return {'success': True}
