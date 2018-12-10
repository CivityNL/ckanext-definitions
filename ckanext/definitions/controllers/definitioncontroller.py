import ckan.lib.base as base
import ckan.model as model
import ckan.authz as authz
import ckanext.user_extra.logic.action.get as get
import logging
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.common import OrderedDict
import ckan.logic as logic
from six import string_types
from urllib import urlencode
import ckan.lib.search as search
import ckan.lib.helpers as h
import ckan.plugins as plugins

import ckanext.definitions.model.definition as definition_model

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
_check_access = logic.check_access

log = logging.getLogger(__name__)
abort = base.abort


class DefinitionController(base.BaseController):

    def search(self):
        '''Render this package's public activity stream page.'''

        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user, 'for_view': True,
                   'auth_user_obj': toolkit.c.userobj}

        extra_vars = {}
        extra_vars['definitions'] = toolkit.get_action('definition_list')(
            context, {})
        return toolkit.render('definition/index.html', extra_vars=extra_vars)

    def dataset_definition(self, id):
        '''Render this package's public activity stream page.'''

        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user, 'for_view': True,
                   'auth_user_obj': toolkit.c.userobj}
        data_dict = {'id': id}
        try:
            toolkit.c.pkg_dict = toolkit.get_action('package_show')(context,
                                                                    data_dict)
            toolkit.c.pkg = context['package']
        except toolkit.ObjectNotFound:
            abort(404, toolkit._('Dataset not found'))
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to read dataset %s') % id)

        return toolkit.render('package/definition.html')

    def read(self, definition_id, limit=20):

        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user,
                   # 'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        data_dict = {'id': definition_id}

        # unicode format (decoded from utf8)
        toolkit.c.q = toolkit.request.params.get('q', '')

        try:
            # Do not query for the group datasets when dictizing, as they will
            # be ignored and get requested on the controller anyway
            data_dict['include_datasets'] = False

            toolkit.c.definition_dict = toolkit.get_action('definition_show')(context, data_dict)
            # toolkit.c.definition = context['definition']
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            abort(404, toolkit._('Definition not found'))

        self._read(definition_id, limit)
        return toolkit.render('definition/read.html')

    def _read(self, definition_id, limit):
        ''' This is common code used by both read and bulk_process'''


        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user,
                   # 'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = toolkit.c.q = toolkit.request.params.get('q', '')
        # Search within group

        fq = 'definition:"%s"' % toolkit.c.definition_dict.get('id')

        toolkit.c.description_formatted = \
            toolkit.h.render_markdown(toolkit.c.definition_dict.get('description'))

        context['return_query'] = True

        page = toolkit.h.get_page_number(toolkit.request.params)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in toolkit.request.params.items()
                         if k != 'page']
        sort_by = toolkit.request.params.get('sort', None)

        def search_url(params):
            controller = 'ckanext.definitions.controllers.definitioncontroller:DefinitionController'
            action = 'bulk_process' if toolkit.c.action == 'bulk_process' else 'read'
            url = toolkit.h.url_for(controller=controller, action=action, definition_id=definition_id)
            params = [(k, v.encode('utf-8') if isinstance(v, string_types)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)

        def drill_down_url(**by):
            return toolkit.h.add_url_param(alternative_url=None,
                                   controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController', action='read',
                                   extras=dict(definition_id=toolkit.c.definition_dict.get('id')),
                                   new_params=by)

        toolkit.c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            controller = 'ckanext.definitions.controllers.definitioncontroller:DefinitionController'
            return toolkit.h.remove_url_param(key, value=value, replace=replace,
                                      controller=controller, action='read',
                                      extras=dict(definition_id=toolkit.c.definition_dict.get('name')))

        toolkit.c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            toolkit.c.fields = []
            toolkit.c.fields_grouped = {}
            search_extras = {}
            for (param, value) in toolkit.request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        toolkit.c.fields.append((param, value))
                        q += ' %s: "%s"' % (param, value)
                        if param not in toolkit.c.fields_grouped:
                            toolkit.c.fields_grouped[param] = [value]
                        else:
                            toolkit.c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            facets = OrderedDict()

            default_facet_titles = {'definition': toolkit._('Definition'),
                                    'groups': toolkit._('Groups'),
                                    'tags': toolkit._('Tags'),
                                    'res_format': toolkit._('Formats'),
                                    'license_id': toolkit._('Licenses')}

            for facet in toolkit.h.facets():
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Facet titles
            for plugin in plugins.PluginImplementations(plugins.IFacets):
                facets = plugin.dataset_facets(facets, 'dataset')

            toolkit.c.facet_titles = facets

            data_dict = {
                'q': q,
                'fq': fq,
                'include_private': True,
                'facet.field': facets.keys(),
                'rows': limit,
                'sort': sort_by,
                'start': (page - 1) * limit,
                'extras': search_extras
            }

            context_ = dict((k, v) for (k, v) in context.items()
                            if k != 'schema')
            log.info('query is = {0}'.format(data_dict))
            query = toolkit.get_action('package_search')(context_, data_dict)

            toolkit.c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )

            toolkit.c.definition_dict['package_count'] = query['count']

            toolkit.c.search_facets = query['search_facets']
            toolkit.c.search_facets_limits = {}
            for facet in toolkit.c.search_facets.keys():
                limit = int(toolkit.request.params.get('_%s_limit' % facet,
                                                       toolkit.config.get('search.facets.default', 10)))
                toolkit.c.search_facets_limits[facet] = limit
                toolkit.c.page.items = query['results']

                toolkit.c.sort_by_selected = sort_by

        except search.SearchError as se:
            log.error('Definition search error: %r', se.args)
            toolkit.c.query_error = True
            toolkit.c.page = toolkit.h.Page(collection=[])

        toolkit.c.definition_id = definition_id

    def new(self, data=None, errors=None, error_summary=None):

        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user,
                   'save': 'save' in toolkit.request.params,
                   'parent': toolkit.request.params.get('parent', None)}

        # Authorization Check
        # try:
        #     self._check_access('definition_create', context)
        # except NotAuthorized:
        #     abort(403, _('Unauthorized to create a group'))

        if context['save'] and not data and toolkit.request.method == 'POST':
            return self._save_new(context)

        data = data or {}
        if not data.get('image_url', '').startswith('http'):
            data.pop('image_url', None)

        errors = errors or {}
        error_summary = error_summary or {}
        extra_vars = {'data': data, 'errors': errors,
                      'error_summary': error_summary, 'action': 'new'}

        # setup_template_variables equivalent
        toolkit.c.data = data
        toolkit.c.errors = errors
        toolkit.c.error_summary = error_summary
        toolkit.c.action = 'new'

        toolkit.c.form = toolkit.render('definition/snippets/definition_form.html',
                                        extra_vars=extra_vars)
        return toolkit.render('definition/new.html', extra_vars=extra_vars)

    def _save_new(self, context):
        try:
            data_dict = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(toolkit.request.params))))
            context['message'] = data_dict.get('log_message', '')
            data_dict['users'] = [
                {'name': toolkit.c.user, 'capacity': 'admin'}]
            definition = toolkit.get_action('definition_create')(context,
                                                                 data_dict)

            # Redirect to the appropriate _read route for the definition
            toolkit.h.redirect_to('/definition')
            # toolkit.h.redirect_to('/definition', id=definition['id'])
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized) as e:
            toolkit.abort(404, _('Definition not found'))
        except dict_fns.DataError:
            toolkit.abort(400, _(u'Integrity Error'))
        except toolkit.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)

    def edit(self, definition_id, data=None, errors=None, error_summary=None):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user,
                   'save': 'save' in toolkit.request.params,
                   'for_edit': True,
                   'parent': toolkit.request.params.get('parent', None)
                   }
        data_dict = {'id': definition_id, 'include_datasets': False}

        if context['save'] and not data and toolkit.request.method == 'POST':
            return self._save_edit(definition_id, context)

        try:
            data_dict['include_datasets'] = False
            old_data = toolkit.get_action('definition_show')(context, data_dict)
            toolkit.c.definitionlabel = old_data.get('title')
            toolkit.c.definitionid= old_data.get('name')
            data = data or old_data
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            abort(404, _('Definition not found'))

        definition = context.get("definition")
        toolkit.c.definition = definition
        toolkit.c.definition_dict = toolkit.get_action('definition_show')(context, data_dict)

        try:
            toolkit.check_access('group_update', context)
        except toolkit.NotAuthorized:
            abort(403, _('User %r not authorized to edit %s') % (toolkit.c.user, definition_id))

        errors = errors or {}
        extra_vars = {'data': data, 'errors': errors,
                'error_summary': error_summary}


        # setup_template_variables equivalent
        toolkit.c.data = data
        toolkit.c.errors = errors
        toolkit.c.error_summary = error_summary

        toolkit.c.form = toolkit.render('definition/snippets/definition_form.html', extra_vars=extra_vars)
        return toolkit.render('definition/edit.html')

    def _save_edit(self, definition_id, context):
        try:
            data_dict = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(toolkit.request.params))))
            context['message'] = data_dict.get('log_message', '')
            data_dict['id'] = definition_id
            context['allow_partial_update'] = True
            definition = toolkit.get_action('definition_update')(context, data_dict)

            h.redirect_to('definition_read', definition_id=definition_id)
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized) as e:
            abort(404, _('Group not found'))
        except dict_fns.DataError:
            abort(400, _(u'Integrity Error'))
        except toolkit.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.edit(definition_id, data_dict, errors, error_summary)

    def delete(self, definition_id):
        if 'cancel' in toolkit.request.params:
            toolkit.h.redirect_to('definition_edit', definition_id=definition_id)

        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}

        try:
            toolkit.check_access('group_delete', context, {'id': definition_id})
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to delete group %s') % '')

        try:
            if toolkit.request.method == 'POST':
                toolkit.get_action('definition_delete')(context, {'id': definition_id})
                toolkit.h.flash_notice(toolkit._('Definition has been deleted.'))
                toolkit.h.redirect_to('definition_search')
            toolkit.c.definition_dict = toolkit.get_action('definition_show')(context, {'id': definition_id})
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to delete definition %s') % '')
        except toolkit.ObjectNotFound:
            abort(404, toolkit._('Definition not found'))
        except toolkit.ValidationError as e:
            toolkit.h.flash_error(e.error_dict['message'])
            toolkit.h.redirect_to(controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController', action='read', id=definition_id)
        return toolkit.render_template('definition/confirm_delete.html')
