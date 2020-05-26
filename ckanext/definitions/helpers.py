from ckan.plugins import toolkit
import logging
import ckan.model as model

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
    print 'definition_enabled_facet_show'
    print facet_item

    if facet_item['name'] == 'True':
        return 'Ja'
    return 'Nee'


def maker_facet_list_help(facet_item):
    try:
        maker = toolkit.get_action('user_show')({}, {'id': facet_item['name']})
        if maker['fullname'] is not None:
            return maker['fullname']
    except toolkit.ObjectNotFound:
        return facet_item['name']


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
