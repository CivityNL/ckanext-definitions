import ckan.logic as logic
import logging
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)
NotFound = logic.NotFound


def definition_update(context, data_dict):
    '''
    Only for Data Officers
    '''

    _data_dict = {'user_id': context['user']}
    result = toolkit.h.is_data_officer(context, _data_dict)

    return {'success': result}


def data_officer_manage(context, data_dict):
    '''
    SysAdmin Only
    '''
    return {'success': False}
