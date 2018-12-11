from ckan.plugins import toolkit
import logging

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Only for Data Officers
    '''

    _data_dict = {'user_id': context['user']}
    log.info('_data_dict = {0}'.format(_data_dict))
    result = toolkit.h.is_data_officer(context, _data_dict)
    log.info('result = {0}'.format(result))

    return {'success': result}


def data_officer_create(context, data_dict):
    '''
    SysAdmin Only
    '''
    return {'success': False}
