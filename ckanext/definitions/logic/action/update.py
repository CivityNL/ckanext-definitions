import ckanext.definitions.model.definition as definition_model
import ckan.lib.dictization as dictization
import ckan.plugins.toolkit as toolkit
import datetime
import logging
from ckanext.definitions.logic.action import reindex_packages

log = logging.getLogger(__name__)


def definition_update(context, data_dict):
    '''
    Updates a definition
    :param context:
    :param data_dict: contains 'id', 'label', 'description', 'url', 'enabled'
    :return: the updated definition
    '''
    session = context['session']
    model = context['model']
    user = context['user']
    result = None

    errors = {}
    mandatory_fields = ['id', 'label', 'description']
    for key in mandatory_fields:
        if (key not in data_dict) or not data_dict[key]:
            errors[key] = [toolkit._('Missing value')]

    if errors:
        session.rollback()
        raise toolkit.ValidationError(errors)

    _disabled = False

    definition_id = data_dict['id']
    definition = definition_model.Definition.get(definition_id=definition_id)

    definition.label = data_dict['label']
    definition.description = data_dict['description']
    definition.url = data_dict['url']

    _enabled = toolkit.asbool(data_dict['enabled'])
    _disabled = not _enabled and definition.enabled
    _existing_package_ids = []
    if _disabled:
        _existing_package_ids = [package.id for package in definition.packages_all]
        definition.packages_all = []

    definition.enabled = _enabled
    definition.modified_date = datetime.datetime.utcnow()

    definition.discipline = data_dict.get('discipline', None)
    definition.expertise = data_dict.get('expertise', None)

    session.add(definition)
    session.flush()

    user_obj = model.User.by_name(user)
    if user_obj:
        user_id = user_obj.id
    else:
        user_id = 'not logged in'
    activity = definition.activity_stream_item('changed', user_id)
    session.add(activity)
    session.commit()

    if _disabled:
        reindex_packages(_existing_package_ids)

    result = dictization.table_dictize(definition, context)

    return result
