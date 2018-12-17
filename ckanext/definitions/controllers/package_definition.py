import ckan.lib.base as base
import ckan.model as model
import logging
import ckan.plugins.toolkit as toolkit

import ckan.logic as logic


tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)
abort = base.abort




class PackageDefinitionController(base.BaseController):



    def index(self, package_id):
        '''Render this package's definition page.'''

        extra_vars = _load_package_and_definitions(package_id)
        return toolkit.render('package/definition_index.html', extra_vars=extra_vars)


    def edit(self, package_id):
        '''Render this package's definition page.'''

        extra_vars = _load_package_and_definitions(package_id)
        return toolkit.render('package/definition_edit.html', extra_vars=extra_vars)


    def new(self, package_id):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}
        definition_id = toolkit.request.params.get('definition_id', None)

        try:
            toolkit.check_access('package_update', context, {'id':package_id})
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to add definition to dataset %s') % '')

        data_dict = {'package_id': package_id, 'definition_id': definition_id}
        toolkit.get_action('package_definition_create')(context, data_dict)

        return toolkit.redirect_to('dataset_definition_edit', package_id=package_id)


    def delete(self, package_id, definition_id):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}

        try:
            toolkit.check_access('package_update', context, {'id':package_id})
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to delete definition from dataset %s') % '')

        data_dict = {'package_id': package_id, 'definition_id': definition_id}
        toolkit.get_action('package_definition_delete')(context, data_dict)

        return toolkit.redirect_to('dataset_definition_edit', package_id=package_id)

def _load_package_and_definitions(package_id):

    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user, 'for_view': True,
               'auth_user_obj': toolkit.c.userobj}
    data_dict = {'id': package_id}

    try:
        toolkit.c.pkg_dict = toolkit.get_action('package_show')(context, data_dict)
        toolkit.c.pkg = context['package']

        pkg_definitions = toolkit.get_action('search_definitions_by_package')(context, {
            'package_id': package_id})

        extra_vars = {'pkg_definitions': pkg_definitions}

    except toolkit.ObjectNotFound:
        abort(404, toolkit._('Dataset not found'))
    except toolkit.NotAuthorized:
        abort(403, toolkit._('Unauthorized to read dataset %s') % package_id)

    return extra_vars
