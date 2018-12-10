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
