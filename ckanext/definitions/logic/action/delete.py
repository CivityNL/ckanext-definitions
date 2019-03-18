# encoding: utf-8

'''API functions for deleting data from CKAN.'''
import ast
import logging

import ckan.lib.jobs as jobs
import ckan.logic
import ckan.model as model
from ckanext.definitions.constants import EMAIL_DELETE_DEFINITION_MULTI,EMAIL_DELETE_DEFINITION_SINGLE
from ckan.common import _
from ckan.plugins import toolkit

import ckanext.definitions.model.definition as definitions_model

log = logging.getLogger('ckan.logic')

validate = ckan.lib.navl.dictization_functions.validate

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
ValidationError = ckan.logic.ValidationError
NotFound = ckan.logic.NotFound
_get_or_bust = ckan.logic.get_or_bust
_get_action = ckan.logic.get_action


def definition_delete(context, data_dict):
    '''Delete a definition.

    You must be a Data Officer to delete definitions.
    Also deletes all Package_definitions from the packages associated

    :param id: the id of the definition
    :type id: string

    '''

    model = context['model']
    if not data_dict.has_key('id') or not data_dict['id']:
        raise ValidationError({'id': _('id not in data')})

    toolkit.check_access('definition_delete', context, data_dict)

    definition_id = data_dict['id']

    # check if definition exists
    definition_obj = definitions_model.Definition.get(definition_id)
    if definition_obj is None:
        raise NotFound(_('Could not find definition "%s"') % definition_id)

    _delete_all_package_definitions_for_definition(context, data_dict)

    # Delete the actual Definition
    definition_obj.delete()
    model.repo.commit()

    return {'success': True,
            'msg': 'successfully deleted definition {0}'.format(definition_id)}


# NOT AN PUBLIC ACTION
def _delete_all_package_definitions_for_definition(context, data_dict):
    if not data_dict.has_key('id') or not data_dict['id']:
        raise ValidationError({'id': _('id not in data')})

    definition_id = data_dict['id']

    # check if definition exists
    definition_obj = definitions_model.Definition.get(definition_id)
    if definition_obj is None:
        raise toolkit.ObjectNotFound(
            _('Could not find definition "%s"') % definition_id)

    # Delete all package_definitions associated
    context['ignore_auth'] = True
    data_dict_2 = {'definition_id': definition_id, 'all_fields': True}
    pkg_list = toolkit.get_action('search_packages_by_definition')(context,
                                                                   data_dict_2)


    # Aggregate Owner/Mandated emails for the same person
    # create a String that is a list of "[title] --> [link]"

    # gathers the emails to send, aggregating per email_receiver
    emails_per_receiver = dict()
    for package in pkg_list:
        log.info('TITLE = {0}'.format(package['title']))

    for package in pkg_list:
        _data_dict = {'package_id': package['id'],
                      'definition_id': definition_id}

        toolkit.get_action('package_definition_delete')(context.copy(), _data_dict)

        url_for_dataset = toolkit.url_for(controller='package',
                                          action='read',
                                          id=package['name'],
                                          _external=True)

        # Email Notification for Mandated or Owner
        if package['state'] == 'active':
            try:
                receiver_email = _get_receiver_email(
                    package['mandated'])
            except (KeyError, AttributeError):
                # Send email to Owner
                receiver_email = _get_receiver_email(
                    package['owner'])


            string_to_append = '{0} --> {1}<br>'.format(
                package['title'], url_for_dataset)

            if receiver_email in emails_per_receiver:
                emails_per_receiver[receiver_email].append(string_to_append)

            else:
                emails_per_receiver[receiver_email] = [string_to_append]

    for receiver_email in emails_per_receiver:
        if len(emails_per_receiver[receiver_email]) > 1:
            list_of_datasets_string = ''
            for dataset_link_string in emails_per_receiver[receiver_email]:
                list_of_datasets_string = list_of_datasets_string + dataset_link_string

            subject = EMAIL_DELETE_DEFINITION_MULTI['subject']
            message = EMAIL_DELETE_DEFINITION_MULTI['message'].format(
                definition_obj.label, list_of_datasets_string)
        else:
            subject = EMAIL_DELETE_DEFINITION_SINGLE['subject']
            message = EMAIL_DELETE_DEFINITION_SINGLE['message'].format(
                definition_obj.label, emails_per_receiver[receiver_email])
        # Send the email
        toolkit.h.workflow_send_email(receiver_email, subject, message)


##############################################################
##############################################################
#  Data Officer
##############################################################
##############################################################


def data_officer_delete(context, data_dict):
    '''
    Removes the role Data Officer from a User
    :param context:
    :param data_dict: contains 'user_id'
    :return: the definition added to the DB
    '''

    user_id = data_dict['user_id']
    user_extras = \
        toolkit.get_action('user_extra_show')(context, {"user_id": user_id})[
            'extras']

    for extra_dict in user_extras:
        if extra_dict['key'] == 'Data Officer':
            _data_dict = {"user_id": user_id,
                          "extras": [{"key": "Data Officer", "new_value": ""}]}
            result = toolkit.get_action('user_extra_update')(context,
                                                             _data_dict)
            return "User removed Successfuly from the Data Officers List."
    return "User is not a Data Officer"


def package_definition_delete(context, data_dict):
    '''
    Removes the role Definitions from the dataset
    :param context:
    :param data_dict: contains 'package_id' and 'definition_id'
    :return: True if Successfull, otherwise False
    '''

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
    # Should we check this?
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
            return {'success': False, 'msg': 'Definition Not Found'}
    except toolkit.ValidationError:
        return {'success': False, 'msg': 'Definition Not Found'}
    except SyntaxError:
        return {'success': False, 'msg': 'Definition Not Found'}

    #  Remove the definition if it is found
    if definition_id in definitions:
        definitions.remove(definition_id)

        pkg_dict['definition'] = unicode(definitions)

        # TODO Replace with patch?
        pkg_dict = toolkit.get_action("package_update")(context,
                                                        data_dict=pkg_dict)
        return pkg_dict

    return pkg_dict


def _get_receiver_email(user_id):
    group_mailbox = toolkit.h.catalogthehague_get_group_mailbox_for_user(
        user_id)
    if group_mailbox:
        return group_mailbox
    else:
        return model.User.get(user_id).email
