from ckan.plugins import toolkit

import ckanext.definitions.model.definition as definition_model
import ckan.lib.dictization as dictization
import logging

log = logging.getLogger(__name__)


def definition_create(context, data_dict):
    '''
    Creates a definition in database
    :param context:
    :param data_dict: contains 'label', 'description', 'url', 'enabled'
    :return: the definition added to the DB
    '''
    model = context['model']
    user = context['user']

    label = data_dict.get('label', '')
    description = data_dict.get('description', '')
    url = data_dict.get('url', '')
    enabled = data_dict.get('enabled', True)

    # Authorization Check
    # _check_access('definition_create', context, data_dict)

    # Validators
    errors = {}

    if not label:
        if 'label' in errors:
            errors['label'].append(toolkit._('Value cannot be empty.'))
        else:
            errors['label'] = ['Value cannot be empty.']

    if not description:
        if 'description' in errors:
            errors['description'].append(toolkit._('Value cannot be empty.'))
        else:
            errors['description'] = [toolkit._('Value cannot be empty.')]

    if errors:
        model.Session.rollback()
        raise toolkit.ValidationError(errors)


    definition = definition_model.Definition(label=data_dict['label'],
                                             description=data_dict['description'],
                                             url=data_dict['url'],
                                             enabled=data_dict['enabled'],
                                             creator_id=user
                                             )
    model.Session.add(definition)
    model.Session.commit()

    result = dictization.table_dictize(definition, context)
    return result




def add_package_definition(context, data_dict):
    # pkg_dict does not bring up all fields to UI
    pkg_dict = toolkit.get_action("package_show")(data_dict={"id": data_dict['id'], "internal_call": True})

    modifior_id = context['model'].User.get(context['user']).id

    definition_model.add_package_definition(context['session'], pkg_dict, modifior_id=modifior_id)
