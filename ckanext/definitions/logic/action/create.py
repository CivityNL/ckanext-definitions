from ckan.plugins import toolkit
from ckanext.definitions.model import Definition
import logging
from ckanext.definitions.logic.action import reindex_package, create_definition_package_relationship_activities
from ckan.model import Activity


log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Creates a definition in database
    :param context:
    :param data_dict: contains 'label', 'description', 'url', 'enabled'
    :return: the definition added to the DB
    '''
    model = context['model']
    session = context['session']
    user = context['user']
    user_id = getattr(context['auth_user_obj'], 'id')

    definitions_id = data_dict.get('id', None)
    label = data_dict.get('label', '')
    description = data_dict.get('description', '')

    # Authorization Check
    toolkit.check_access('definition_create', context, data_dict)

    # Validators
    errors = {}

    if not label:
        if 'label' in errors:
            errors['label'].append(toolkit._('Value cannot be empty.'))
        else:
            errors['label'] = [toolkit._('Value cannot be empty.')]
    if not description:
        if 'description' in errors:
            errors['description'].append(toolkit._('Value cannot be empty.'))
        else:
            errors['description'] = [toolkit._('Value cannot be empty.')]
    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)

    definition = Definition(
        definition_id=definitions_id,
        label=data_dict['label'],
        description=data_dict['description'],
        url=data_dict['url'],
        enabled=toolkit.asbool(data_dict['enabled']),
        creator_id=user_id,

        #additional metadata from customers
        discipline=data_dict.get('discipline', None),
        expertise=data_dict.get('expertise', None)
    )

    session.add(definition)
    session.flush()

    user_obj = model.User.by_name(user)
    if user_obj:
        user_id = user_obj.id
    else:
        user_id = 'not logged in'
    activity = definition.activity_stream_item('new', user_id)
    session.add(activity)
    session.commit()

    result = definition.to_dict(context)
    return result


def definition_data_officer_create(context, data_dict):
    # check for valid input
    user_id = toolkit.get_or_bust(data_dict, 'user_id')

    toolkit.check_access('definition_data_officer_create', context, data_dict)

    # check if user exists
    try:
        user_dict = toolkit.get_action("user_show")(context, {"id": user_id, "include_plugin_extras": True})
    except toolkit.ObjectNotFound as exception:
        return {'success': False, 'msg': exception.message}

    user_plugin_extras = user_dict.get('plugin_extras', {}) or {}
    definition_plugin_extras = user_plugin_extras.get('definition', {})

    if 'data_officer' in definition_plugin_extras and definition_plugin_extras.get('data_officer'):
        return {'success': True, 'msg': 'User is already a Data Officer'}
    else:
        definition_plugin_extras['data_officer'] = True
        user_plugin_extras['definition'] = definition_plugin_extras
        toolkit.get_action('user_patch')(dict(context, ignore_auth=True), {"id": user_id, 'plugin_extras': user_plugin_extras})
        return {'success': True, 'msg': 'User added Successfully to the Data Officers List.'}


def definition_package_relationship_create(context, data_dict):
    # check for valid input
    print("package_definition_create [{}]".format(data_dict))
    model = context['model']
    session = context['session']
    user = context['user']

    package_id, definition_id = toolkit.get_or_bust(data_dict, ['package_id', 'definition_id'])

    package = model.Package.get(package_id)
    if package is None:
        raise toolkit.ObjectNotFound(toolkit._('Package not found'))
    definition = Definition.get(definition_id)
    if definition is None:
        raise toolkit.ObjectNotFound(toolkit._('Definition not found'))

    if package.id in [p.id for p in definition.packages_all]:
        raise toolkit.ValidationError(toolkit._("Package {} is already linked to definition {}".format(
            package.id, definition.id
        )))

    definition.packages_all.append(package)
    session.add(definition)
    session.flush()
    create_definition_package_relationship_activities(session, definition, package, user, "added")
    session.commit()
    pkg_dict = reindex_package(package.id)

    return pkg_dict
