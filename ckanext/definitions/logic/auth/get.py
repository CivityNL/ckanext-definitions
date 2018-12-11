import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
NotFound = logic.NotFound
import logging
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
    return {'success': True}
