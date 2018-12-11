import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import logging

NotFound = logic.NotFound
log = logging.getLogger(__name__)


def definition_read(context, data_dict):
    '''
    Authorization Info...
    '''
    return {'success': True}


def data_officer_read(context, data_dict):
    '''
    Publicly available
    '''
    return {'success': False}
