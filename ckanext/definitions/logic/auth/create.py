from ckan.plugins import toolkit
import logging

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Only for Data Officers
    '''

    _data_dict = {'user_id': context['user']}
    result = toolkit.h.is_data_officer(context, _data_dict)
    return {'success': result}


def data_officer_create(context, data_dict):
    '''
    SysAdmin Only
    '''
    return {'success': False}
