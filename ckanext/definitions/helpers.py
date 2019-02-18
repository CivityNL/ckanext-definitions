from ckan.plugins import toolkit
import logging

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
