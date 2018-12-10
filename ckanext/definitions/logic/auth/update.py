'''
Created on July 2nd, 2015

@author: dan
'''

import ckan.logic as logic
import logging
log = logging.getLogger(__name__)
import logic.auth.create as user_extra_create

NotFound = logic.NotFound


def user_extra_update(context, data_dict):
    '''
    A user has access only to his own metainformation (user_extra).
    '''

    return user_extra_create(context, data_dict)
