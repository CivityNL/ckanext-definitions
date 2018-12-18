import ckanext.definitions.model.definition as definition_model
import ckan.lib.dictization as dictization
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import datetime
import sys
import logging

log = logging.getLogger(__name__)
NotFound = logic.NotFound


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

    try:
        definition_id = data_dict['id']
        definition = definition_model.Definition.get(definition_id=definition_id)

        definition.label = data_dict['label']
        definition.description = data_dict['description']
        definition.url = data_dict['url']
        definition.enabled = data_dict['enabled']
        definition.modified_date = datetime.datetime.utcnow()

        # Delete all Package_Definitions with that Definition
        if definition.enabled == 'False':
            log.info('Deleting all Package_Definitions from definition -> {0}'.format(definition_id))

            _data_dict = {'definition_id': definition_id, 'all_fields': True}
            pkg_list = toolkit.get_action('search_packages_by_definition')(context, _data_dict)
            for package in pkg_list:
                _data_dict = {'package_id': package['id'],
                              'definition_id': definition_id}
                toolkit.get_action('package_definition_delete')(context, _data_dict)


        session.add(definition)
        session.commit()
        result = dictization.table_dictize(definition, context)
    except:
        print sys.exc_info()[0]

    return result

