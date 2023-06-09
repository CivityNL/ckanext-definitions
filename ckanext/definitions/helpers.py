import logging
from ckan import model
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def is_data_officer(context, data_dict={}):
    """
    :param: user_id - the User id or username
    :type: string
    :return: True if an User is a Data Officer, or False otherwise.
    :type: boolean
    """
    # TODO get or bust
    user_id = toolkit.get_converter('convert_user_name_or_id_to_id')(data_dict['user_id'], context)
    user_extras = toolkit.get_action('user_extra_show')(context, {"user_id": user_id})['extras']

    for extra_dict in user_extras:
        if extra_dict['key'] == 'Data Officer' and extra_dict['value'] == 'True':
            return True

    return False


def definition_list_choices():
    """
    Get the Definitions List and converts it to the Scheming Choices format
    """
    choices = []

    # context = {'user': ''}
    definitions = toolkit.get_action('definition_list')({}, {'all_fields': True})

    for definition in definitions:
        choice = dict(value=definition['label'], label=definition['display_name'])
        choices.append(choice)

    return choices


def definition_enabled_facet_show(facet_item):
    log.debug('definition_enabled facet: {item}'.format(item=facet_item))

    if facet_item['name'] == 'True':
        return 'Ja'
    return 'Nee'


def user_facet_list_help(facet_item):
    try:
        user = toolkit.get_action('user_show')({'ignore_auth': True}, {'id': facet_item['name']})
    except Exception as ex:
        user = None

    result = facet_item['name']

    if user:
        if user.get('display_name', False):
            result = user['display_name']
        elif user.get('name', False):
            result = user['name']

    return result


def owner_facet_list_help(facet_item):
    try:
        user = toolkit.get_action('user_show')({}, {'id': facet_item['name']})
        if user['fullname'] is not None:
            return user['fullname']
    except toolkit.ObjectNotFound:
        pass
    try:
        organization = toolkit.get_action('organization_show')({}, {'id': facet_item['name']})
        if organization['display_name'] is not None:
            return organization['display_name']
    except toolkit.ObjectNotFound:
        return facet_item['name']


def package_definition_count(pkg_id):
    if not pkg_id:
        raise toolkit.ValidationError(toolkit._('Package Id not provided.'))

    context = {'model': model, 'user': toolkit.c.user or toolkit.c.author}
    package_definitions = toolkit.get_action('search_definitions_by_package')(context, {'package_id': pkg_id})
    return len(package_definitions)


def search_title_only_filter():
    return toolkit.asbool(toolkit.config.get('ckanext.definitions.search_title_only_filter', False))

def show_additional_metadata():
    return toolkit.asbool(toolkit.config.get('ckanext.definitions.show_additional_metadata', False))
