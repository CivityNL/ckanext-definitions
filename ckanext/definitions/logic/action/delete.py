# encoding: utf-8

'''API functions for deleting data from CKAN.'''

import logging

import sqlalchemy as sqla

import ckan.lib.jobs as jobs
import ckan.logic
import ckan.logic.action
import ckan.plugins as plugins
import ckan.lib.dictization.model_dictize as model_dictize
import ckanext.definitions.model.definition as definitions_model
from ckan import authz

from ckan.common import _


log = logging.getLogger('ckan.logic')

validate = ckan.lib.navl.dictization_functions.validate

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
ValidationError = ckan.logic.ValidationError
NotFound = ckan.logic.NotFound
_check_access = ckan.logic.check_access
_get_or_bust = ckan.logic.get_or_bust
_get_action = ckan.logic.get_action


def definition_delete(context, data_dict):
    '''Delete a definition.

    You must be a Data Officer to delete definitions.

    :param id: the id of the definition
    :type id: string

    '''

    model = context['model']

    log.info('model = {0}'.format(model ))
    if not data_dict.has_key('id') or not data_dict['id']:
        raise ValidationError({'id': _('id not in data')})

    definition_id = data_dict['id']

    definition_obj = definitions_model.Definition.get(definition_id)

    if definition_obj is None:
        raise NotFound(_('Could not find definition "%s"') % definition_id)

    # _check_access('definition_delete', context, data_dict)

    definition_obj.delete()
    model.repo.commit()
