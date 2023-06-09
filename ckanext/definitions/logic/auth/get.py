import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


@toolkit.auth_allow_anonymous_access
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


def definition_autocomplete(context, data_dict):
    '''
    Publicly available
    '''
    return {'success': True}