import logging
from ckan import model
from ckan.plugins import toolkit
from ckan.lib.search import query_for

log = logging.getLogger(__name__)


def is_data_officer(user_name_or_id):
    """
    :param: user_id - the User id or username
    :type: string
    :return: True if an User is a Data Officer, or False otherwise.
    :type: boolean
    """
    # TODO get or bust

    if not user_name_or_id:
        return False

    site_user = toolkit.get_action(u"get_site_user")({u"ignore_auth": True}, {})
    context = {u"user": site_user[u"name"]}
    user_dict = toolkit.get_action('user_show')(context, {"id": user_name_or_id, "include_plugin_extras": True})

    user_plugin_extras = user_dict.get('plugin_extras', {}) or {}
    definition_plugin_extras = user_plugin_extras.get('definition', {})

    return definition_plugin_extras.get("data_officer", False)


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


def get_packages_for_definition(context, definition_):
    # Ask SOLR for the list of packages for this definition
    q = {
        'facet': 'false',
        'rows': 0,
        'fq': '+definitions:"{0}"'.format(definition_.id),
        'include_private': True
    }

    # package_search limits 'rows' anyway, so this is only if you
    # want even fewer
    try:
        packages_limit = context['limits']['packages']
    except KeyError:
        del q['rows']  # leave it to package_search to limit it
    else:
        q['rows'] = packages_limit

    search_context = dict((k, v) for (k, v) in context.items() if k != 'schema')
    search_results = toolkit.get_action('package_search')(search_context, q)
    return search_results['results']
