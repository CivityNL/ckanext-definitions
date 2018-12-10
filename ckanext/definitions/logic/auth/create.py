'''
Created on August 30th, 2018

@author: niek
'''

from ckan.plugins import toolkit
import ckan.logic as logic
_check_access = logic.check_access

import logging
log = logging.getLogger(__name__)


def user_extra_create(context, data_dict):
    '''
    A user has access only to his own metainformation (user_extra).
    '''
    # print "I was also here"
    user = context.get('auth_user_obj') 
    # print 'user logged in -> ' + user
    #print 'nutryiong to access page of-> ' + data_dict.get('user_id', '')
    print('user_extra_create')
    # print(context.user) 
    print(user.id)
    print(data_dict.get('user_id', ''))
    if user.id == data_dict.get('user_id', ''):
        # log.info('bitches')
        return {
            'success': True
        }

    # log.info('bitches 2')
    return {
        'success': False,
        'msg': toolkit._('Not authorized to perform this request')
    }
