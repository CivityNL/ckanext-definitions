from ckan.plugins import toolkit
import logging

log = logging.getLogger(__name__)


def is_data_officer(context, data_dict={}):
    """
    :param: user_id - the User id or username
    :type: string
    :return: True if an User is a Data Officer, or False otherwise.
    :type: boolean
    """
    # TODO get or bust
    log.info('is_data_officer')

    user_id = toolkit.get_converter('convert_user_name_or_id_to_id')(data_dict['user_id'], context)

    log.info('user_id = {0}'.format(user_id))

    user_extras = toolkit.get_action('user_extra_show')(context, {"user_id": user_id})['extras']
    log.info('user_extras = {0}'.format(user_extras))

    for extra_dict in user_extras:
        log.info('extra_dict = {0}'.format(extra_dict))
        if extra_dict['key'] == 'Data Officer' and extra_dict['value'] == 'True':
            log.info('1')
            return True
        else:
            log.info('2')
            return False

    log.info('3')
    return False

