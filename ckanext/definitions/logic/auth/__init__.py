import logging
log = logging.getLogger(__name__)


def auth_is_data_officer(context):
    auth_user_obj = context.get("auth_user_obj", None)
    log.info("auth_is_data_officer :: auth_user_obj={}".format(auth_user_obj))
    return auth_user_obj is not None and auth_user_obj.plugin_extras


def definition_data_officer_manage(context, data_dict):
    return {'success': False}
