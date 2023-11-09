import ckanext.definitions.model.definition as definition_model
from ckanext.definitions.logic.action.delete import _delete_all_package_definitions_for_definition
import ckan.lib.dictization as dictization
import ckan.plugins.toolkit as toolkit
import datetime
import sys
import logging

log = logging.getLogger(__name__)


def definition_update(context, data_dict):
    '''
    Updates a definition
    :param context:
    :param data_dict: contains 'id', 'label', 'description', 'url', 'enabled'
    :return: the updated definition
    '''
    session = context['session']
    # model = context['model']
    result = None

    errors = {}
    mandatory_fields = ['id', 'label', 'description']
    for key in mandatory_fields:
        if (key not in data_dict) or not data_dict[key]:
            errors[key] = [toolkit._('Missing value')]

    if errors:
        session.rollback()
        raise toolkit.ValidationError(errors)

    try:
        definition_id = data_dict['id']
        definition = definition_model.Definition.get(definition_id=definition_id)

        definition.label = data_dict['label']
        definition.description = data_dict['description']
        definition.url = data_dict['url']
        definition.display_name = definition.label + ' - ' + definition.description
        definition.enabled = toolkit.asbool(data_dict['enabled'])
        definition.modified_date = datetime.datetime.utcnow()

        definition.discipline = data_dict.get('discipline', None)
        definition.expertise = data_dict.get('expertise', None)

        # session.add(definition)
        session.commit()
        result = dictization.table_dictize(definition, context)
    except:
        print(sys.exc_info()[0])

    return result
