from ckan.plugins import toolkit
import logging

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Only for Data Officers
    '''

    return {'success': toolkit.h.is_data_officer(context,
                                                 {'user_id': context['user']})}


def data_officer_create(context, data_dict):
    '''
    SysAdmin Only
    '''
    return {'success': False}
