import ckan.lib.base as base
import ckan.model as model
import logging
import ckan.plugins.toolkit as toolkit

import ckan.logic as logic
from ckanext.definitions.model import Definition

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)
abort = base.abort


def read(package_id):
    """Render this package's definition page."""

    extra_vars = _load_package_and_definitions(package_id)
    return toolkit.render('package/definitions_read.html',
                          extra_vars=extra_vars)


def edit(package_id):
    """Render this package's definition page."""

    extra_vars = _load_package_and_definitions(package_id)
    return toolkit.render('package/definitions_edit.html',
                          extra_vars=extra_vars)


def new(package_id):
    context = {'model': model, 'session': model.Session, 'user': toolkit.c.user}
    definition_id = toolkit.request.values.get('definition_id', None)

    try:
        toolkit.check_access('package_update', context, {'id': package_id})
    except toolkit.NotAuthorized:
        abort(403, toolkit._(
            'Unauthorized to add definition to dataset %s') % '')

    data_dict = {'package_id': package_id, 'definition_id': definition_id}
    toolkit.get_action('definition_package_relationship_create')(context, data_dict)

    return toolkit.redirect_to('package_definition.edit', package_id=package_id)


def delete(package_id, definition_id):
    context = {'model': model, 'session': model.Session, 'user': toolkit.c.user}

    try:
        toolkit.check_access('package_update', context, {'id': package_id})
    except (toolkit.NotAuthorized, toolkit.ObjectNotFound) as pkg_err:
        abort(403, pkg_err.message)

    data_dict = {'package_id': package_id, 'definition_id': definition_id}
    toolkit.get_action('definition_package_relationship_delete')(context, data_dict)

    return toolkit.redirect_to('package_definition.edit', package_id=package_id)


def _load_package_and_definitions(package_id):
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user, 'for_view': True,
               'auth_user_obj': toolkit.c.userobj}
    data_dict = {'id': package_id}

    extra_vars = {}

    try:
        extra_vars['pkg_dict'] = toolkit.get_action('package_show')(context, data_dict)
    except toolkit.ObjectNotFound:
        abort(404, toolkit._('Dataset not found'))
    except toolkit.NotAuthorized:
        abort(403, toolkit._('Unauthorized to read dataset %s') % package_id)

    return extra_vars
