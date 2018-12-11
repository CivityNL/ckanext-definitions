import ckanext.definitions.model.definition as definitions_model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import logging
import ckan.lib.dictization as dictization

NotFound = logic.NotFound
log = logging.getLogger(__name__)


@toolkit.side_effect_free
def definition_show(context, data_dict):
    '''
    Retrieves definition details based on the definition 'id'
    :param context:
    :param data_dict: contains the definition 'id'
    :return: details of definition
    '''
    definition_id = data_dict.get('id')
    result = definitions_model.Definition.get(definition_id)
    if result is None:
        raise NotFound
    result_dict = dictization.table_dictize(result, context)

    return result_dict

@toolkit.side_effect_free
def definition_list(context, data_dict):
    '''
    Retrieves all the definitions
    :param context:
    :return: List of all definitions
    '''
    all_definitions = definitions_model.Definition.all()
    result_dict = []

    for definition in all_definitions:
        result_dict.append(dictization.table_dictize(definition, context))

    return result_dict

@toolkit.side_effect_free
def data_officer_list(context, data_dict):
    '''
    Retrieves all users which are data officers
    :param context:
    :param include_all_user_info:
    :return: List of all data officers
    '''
    result = []
    user_list = toolkit.get_action('user_list')(context, {})

    for user in user_list:
        user_extras = toolkit.get_action('user_extra_show')(context, {"user_id": user['id']})['extras']
        for extra_dict in user_extras:
            if extra_dict['key'] == 'Data Officer' and extra_dict['value'] == 'True':
                if 'include_all_user_info' in data_dict and data_dict['include_all_user_info']:
                    result.append(user)
                else:
                    user_dict = {
                        "id":user['id'],
                        "name": user['name'],
                        "display_name": user['display_name']
                    }
                    result.append(user_dict)
                break

    return result


