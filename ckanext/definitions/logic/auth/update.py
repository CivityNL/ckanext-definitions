import ckan.logic as logic
import logging
import ckan.plugins.toolkit as toolkit
from ckanext.definitions.logic.auth.create import definition_create

log = logging.getLogger(__name__)
NotFound = logic.NotFound


def definition_update(context, data_dict):
    '''
    Only for Data Officers
    '''
    return definition_create(context, data_dict)


def data_officer_manage(context, data_dict):
    '''
    SysAdmin Only
    '''
    return {'success': False}
