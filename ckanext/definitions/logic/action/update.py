import ckanext.definitions.model.definition as definition_model
import ckan.lib.dictization as dictization
import ckan.logic as logic
import datetime
import sys
import logging

log = logging.getLogger(__name__)
NotFound = logic.NotFound


def definition_update(context, data_dict):
    '''
    Updates a definition record in database
    :param context:
    :param data_dict: contains 'id', 'label', 'description', 'url', 'enabled'
    :return: the updated definition
    '''
    session = context['session']
    # model = context['model']
    result = None

    try:
        definition = definition_model.Definition.get(definition_id=data_dict['id'])

        definition.label = data_dict['label']
        definition.description = data_dict['description']
        definition.url = data_dict['url']
        definition.enabled = data_dict['enabled']
        definition.modified_date = datetime.datetime.utcnow()

        session.add(definition)
        session.commit()
        result = dictization.table_dictize(definition, context)
    except:
        print sys.exc_info()[0]

    return result
