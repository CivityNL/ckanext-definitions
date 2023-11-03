import ast

from ckan.plugins import toolkit
import ckanext.definitions.model.definition as definition_model
import ckan.lib.dictization as dictization
import logging

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Creates a definition in database
    :param context:
    :param data_dict: contains 'label', 'description', 'url', 'enabled'
    :return: the definition added to the DB
    '''
    model = context['model']
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

    definition = definition_model.Definition(
        definition_id=definitions_id,
        label=data_dict['label'],
        description=data_dict['description'],
        url=data_dict['url'],
        enabled=data_dict['enabled'],
        creator_id=user_id,

        #additional metadata from customers
        discipline=data_dict.get('discipline', None),
        expertise=data_dict.get('expertise', None)
    )
    model.Session.add(definition)
    model.Session.commit()

    result = dictization.table_dictize(definition, context)
    return result


def data_officer_create(context, data_dict):
    '''
    Makes a User into a Data Officer
    :param context:
    :param data_dict: contains 'user_id'
    :return: the definition added to the DB
    '''
    # check for valid input
    user_id = toolkit.get_or_bust(data_dict, 'user_id')

    # check if user exists
    try:
        user_dict = toolkit.get_action("user_show")(context, {"id": user_id, "include_plugin_extras": True})
    except toolkit.ObjectNotFound:
        return {'success': False, 'msg': toolkit._('User Not Found')}

    user_plugin_extras = user_dict.get('plugin_extras', {}) or {}
    definition_plugin_extras = user_plugin_extras.get('definition', {})

    if 'data_officer' in definition_plugin_extras and definition_plugin_extras.get('data_officer'):
        return {'success': True, 'msg': 'User is already a Data Officer'}
    else:
        definition_plugin_extras['data_officer'] = True
        user_plugin_extras['definition'] = definition_plugin_extras
        toolkit.get_action('user_patch')(context, {"id": user_id, 'plugin_extras': user_plugin_extras})
        return {'success': True, 'msg': 'User added Successfully to the Data Officers List.'}


def package_definition_create(context, data_dict):
    # check for valid input
    try:
        package_id, definition_id = toolkit.get_or_bust(data_dict,
                                                        ['package_id',
                                                         'definition_id'])
    except toolkit.ValidationError:
        return {'success': False, 'msg': 'Input was not right'}

    # check if package exists
    try:
        pkg_dict = toolkit.get_action("package_show")(
            data_dict={"id": package_id, "internal_call": True})
    except toolkit.ObjectNotFound:
        return {'success': False, 'msg': 'Package Not Found'}

    # check if definition exists
    try:
        toolkit.get_action("definition_show")(data_dict={"id": definition_id})
    except toolkit.ObjectNotFound:
        return {'success': False, 'msg': 'Definition Not Found'}

    #  Check if 'definition' field is already in package
    try:
        definitions = toolkit.get_or_bust(pkg_dict, ['definition'])
        if definitions:
            definitions = ast.literal_eval(definitions)
        else:
            definitions = list()
    except toolkit.ValidationError:
        definitions = list()
    except SyntaxError:
        definitions = list()

    #  Add the new definition in case it does not exist there yet
    if definition_id not in definitions:
        definitions.append(definition_id)

        pkg_dict['definition'] = unicode(definitions)

        # TODO Replace with patch?
        pkg_dict = toolkit.get_action("package_update")(context,
                                                        data_dict=pkg_dict)
        return pkg_dict

    return pkg_dict
