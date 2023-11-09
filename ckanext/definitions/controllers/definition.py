import ckan
import ckan.lib.base as base
import ckan.model as model
import logging
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as dict_fns
from collections import OrderedDict
import ckan.logic as logic
from six import string_types
from urllib.parse import urlencode
from ckan.lib.search import SearchError
import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckanext.definitions.model.definition as definitions_model
import ckanext.definitions.helpers as definition_helpers

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

_ = toolkit._

log = logging.getLogger(__name__)
abort = base.abort

LIMIT = 20


def setup_template_variables(context, data_dict):
    toolkit.c.is_sysadmin = ckan.authz.is_sysadmin(toolkit.c.user)

    ## This is messy as auths take domain object not data_dict
    context_definition = context.get('definition', None)
    definition = context_definition or toolkit.c.definition
    if definition:
        try:
            if not context_definition:
                context['definition'] = definition
                toolkit.check_access('definition_read', context)
            toolkit.c.auth_for_change_state = True
        except toolkit.NotAuthorized:
            toolkit.c.auth_for_change_state = False


def search():

    limit = LIMIT
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user, 'auth_user_obj': toolkit.c.userobj,
               'for_view': True}

    # Set Facets Structure
    facets = OrderedDict()
    facets['creator_id'] = _('Creators')
    facets['enabled'] = _('Enabled')
    facets['label'] = _('Labels')

    # Load facets from additional definition metadata, if
    show_additional_metadata = definition_helpers.show_additional_metadata()
    if show_additional_metadata:
        for metadata in definitions_model.ADDITIONAL_FIELDS:
            facets[metadata] = _(metadata.capitalize())

    page = toolkit.h.get_page_number(toolkit.request.params)
    q = toolkit.request.params.get('q', '')
    sort_by = toolkit.request.params.get('sort', None)
    # store value for holding checkbox state on reload
    search_title_only = toolkit.request.params.get('search_title_only', "false")

    params_nopage = [(k, v) for k, v in toolkit.request.params.items() if k != 'page']

    def remove_field(key, value=None, replace=None):
        alternative_url = '/definition'
        controller = 'ckanext.definitions.controllers.definition:DefinitionController'
        return toolkit.h.remove_url_param(key, value=value,
                                          replace=replace,
                                          controller=controller,
                                          action='search',
                                          alternative_url=alternative_url)

    facet_titles = facets

    # TODO handle URL Params with Facets
    search_dict = {}
    for key in facets:
        if key in toolkit.request.params:
            search_dict[key] = toolkit.request.params.get(key, '')
    try:
        enabled = not toolkit.check_access('definition_update', context)
    except toolkit.NotAuthorized:
        enabled = True


    # # TODO Call search Action function instead of model directly

    search_result = definitions_model.Definition.search(
        search_dict=search_dict, q=q, search_title_only=search_title_only, enabled=enabled)

    # total results
    results = search_result['results']

    # Filtered Results to Show in Page
    start = (page-1) * limit

    query = search_result['query']
    if sort_by == 'desc':
        query = query.order_by(definitions_model.Definition.label.desc())
    else:
        query = query.order_by(definitions_model.Definition.label.asc())
    query = query.limit(limit)
    query = query.offset(start)

    page_collection = query.all()

    # Set Facets Content
    search_facets = search_result['search_facets']
    search_facets_limits = {}
    for facet in search_facets.keys():
        facet_limit = int(toolkit.request.params.get('_%s_limit' % facet,
                                               toolkit.config.get(
                                                   'search.facets.default',
                                                   3)))
        search_facets_limits[facet] = facet_limit


    def search_url(params):
        controller = 'ckanext.definitions.controllers.definition:DefinitionController'
        action = 'bulk_process' if toolkit.c.action == 'bulk_process' else 'search'
        url = toolkit.h.url_for(controller=controller, action=action)
        params = [(k, v.encode('utf-8') if isinstance(v, string_types) else str(v)) for k, v in params]
        return url + u'?' + urlencode(params)

    def pager_url(q=None, page=None):
        params = list(params_nopage)
        params.append(('page', page))
        return search_url(params)

    fields = []
    fields_grouped = {}
    fq = ''
    for (param, value) in toolkit.request.params.items():
        if param not in ['q', 'page', 'sort', 'search_title_only'] \
                and len(value) and not param.startswith('_'):
            fields.append((param, value))
            fq += ' %s:"%s"' % (param, value)
            if param not in fields_grouped:
                fields_grouped[param] = [value]
            else:
                fields_grouped[param].append(value)

    page = h.Page(
        collection=page_collection,
        page=page,
        url=pager_url,
        item_count=search_result['count'],
        items_per_page=limit
    )

    # Set Items
    page.items = results

    extra_vars = {
        'facet_titles': facet_titles,
        'fields': fields,
        'fields_grouped': fields_grouped,
        'page': page,
        'q': q,
        'remove_field': remove_field,
        'search_facets': search_facets,
        'search_facets_limits': search_facets_limits,
        'search_title_only': search_title_only,
        'sort_by_selected': sort_by
    }

    return toolkit.render('definition/index.html', extra_vars=extra_vars)


def read(definition_id, limit=20):
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user,
               'for_view': True}

    try:
        definition_dict = toolkit.get_action('definition_show')(context, {'id': definition_id})
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized, KeyError):
        abort(404, _('Definition not found'))

    extra_vars = _read(definition_dict, limit)
    extra_vars['definition_id'] = definition_id
    return toolkit.render('definition/read.html', extra_vars=extra_vars)


def _read(definition_dict, limit):
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user,
               'for_view': True, 'extras_as_string': True}

    definition_id = definition_dict.get("id")

    q = toolkit.request.params.get('q', '')
    # Search within group
    fq = 'definitions:"%s"' % definition_id

    description_formatted = toolkit.h.render_markdown(definition_dict.get('description'))

    context['return_query'] = True

    page = h.get_page_number(toolkit.request.params)

    # most search operations should reset the page counter:
    params_no_page = [(k, v) for k, v in toolkit.request.params.items() if k != 'page']
    sort_by = toolkit.request.params.get('sort', None)

    def search_url(params):
        url = toolkit.h.url_for('definition.read', definition_id=definition_id)
        params = [(k, v.encode('utf-8') if isinstance(v, string_types) else str(v)) for k, v in params]
        return url + u'?' + urlencode(params)

    def drill_down_url(**by):
        alternative_url = toolkit.h.url_for('definition.read', definition_id=definition_id)
        return toolkit.h.add_url_param(alternative_url=alternative_url, new_params=by)

    def remove_field(key, value=None, replace=None):
        alternative_url = toolkit.h.url_for('definition.read', definition_id=definition_id)
        return toolkit.h.remove_url_param(key, value=value, replace=replace, alternative_url=alternative_url)

    def pager_url(q=None, page=None):
        params = list(params_no_page)
        params.append(('page', page))
        return search_url(params)

    fields = []
    fields_grouped = {}
    search_extras = {}
    query_error = False
    try:
        for (param, value) in toolkit.request.params.items():
            if param not in ['q', 'page', 'sort', 'search_title_only'] \
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

        default_facet_titles = {'organization': toolkit._('Organizations'),
                                'groups': toolkit._('Groups'),
                                'tags': toolkit._('Tags'),
                                'res_format': toolkit._('Formats'),
                                'license_id': toolkit._('Licenses')}

        for facet in h.facets():
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet

        # Facet titles
        for plugin in plugins.PluginImplementations(plugins.IFacets):
            facets = plugin.dataset_facets(facets, None)

        package_search_dict = {
            'q': q,
            'fq': fq,
            'include_private': True,
            'facet.field': [field for field in facets],
            'rows': limit,
            'sort': sort_by,
            'start': (page - 1) * limit,
            'extras': search_extras
        }

        context_ = dict((k, v) for (k, v) in context.items() if k != 'schema')

        query = toolkit.get_action('package_search')(context_, package_search_dict)

        page = h.Page(
            collection=query['results'],
            page=page,
            url=pager_url,
            item_count=query['count'],
            items_per_page=limit
        )

        definition_dict['package_count'] = query['count']

        search_facets = query['search_facets']
        search_facets_limits = {}
        for facet in search_facets.keys():
            limit = int(toolkit.request.params.get('_%s_limit' % facet,
                                                   toolkit.config.get(
                                                       'search.facets.default',
                                                       3)))
            search_facets_limits[facet] = limit
        page.items = query['results']

    except SearchError as se:
        log.error('Group search error: %r', se.args)
        query_error = True
        page = h.Page(collection=[])

    # setup_template_variables(context, {'id': id})

    return {
        'description_formatted': description_formatted,
        'drill_down_url': drill_down_url,
        'remove_field': remove_field,
        'fields': fields,
        'fields_grouped': fields_grouped,
        'facet_titles': facets,
        'page': page,
        'definition_dict': definition_dict,
        'search_facets': search_facets,
        'search_facets_limits': search_facets_limits,
        'sort_by_selected': sort_by,
        'query_error': query_error
    }


def new(data=None, errors=None, error_summary=None):
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user,
               'save': 'save' in toolkit.request.values,
               'parent': toolkit.request.params.get('parent', None)}

    # Authorization Check
    try:
        toolkit.check_access('definition_create', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to create a definition'))

    if context['save'] and not data and toolkit.request.method == 'POST':
        return _save_new(context)

    extra_vars = {'data': data or {}, 'errors': errors or {}, 'error_summary': error_summary or {}, 'action': 'new',
                  'form_snippet': 'definition/snippets/definition_form.html'}
    extra_vars['form_vars'] = dict(extra_vars)

    return toolkit.render('definition/new.html', extra_vars=extra_vars)


def _save_new(context):
    data_dict = None
    try:
        data_dict = clean_dict(dict_fns.unflatten(
            tuplize_dict(parse_params(toolkit.request.values))))
        context['message'] = data_dict.get('log_message', '')
        data_dict['users'] = [
            {'name': toolkit.c.user, 'capacity': 'admin'}]
        toolkit.get_action('definition_create')(context, data_dict)

        # Redirect to the appropriate _read route for the definition
        return toolkit.h.redirect_to('/definition')
        # toolkit.h.redirect_to('/definition', id=definition['id'])
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized) as e:
        toolkit.abort(404, _('Definition not found'))
    except dict_fns.DataError:
        toolkit.abort(400, _(u'Integrity Error'))
    except toolkit.ValidationError as e:
        errors = e.error_dict
        error_summary = e.error_summary
        return new(data_dict, errors, error_summary)


def edit(definition_id, data=None, errors=None, error_summary=None):
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user,
               'save': 'save' in toolkit.request.values,
               'for_edit': True,
               'parent': toolkit.request.values.get('parent', None)
               }
    data_dict = {'id': definition_id, 'include_datasets': False}

    # Authorization Check
    try:
        toolkit.check_access('definition_update', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to edit a definition'))

    if context['save'] and not data and toolkit.request.method == 'POST':
        return _save_edit(definition_id, context)

    try:
        data_dict['include_datasets'] = False
        old_data = toolkit.get_action('definition_show')(context,
                                                         data_dict)
        toolkit.c.definitionlabel = old_data.get('label')
        toolkit.c.definitionid = old_data.get('id')
        data = data or old_data
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        abort(404, _('Definition not found'))

    definition_dict = toolkit.get_action('definition_show')(context, data_dict)

    extra_vars = {'definition_dict': definition_dict, 'data': data or {}, 'errors': errors or {}, 'error_summary': error_summary or {},
                  'form_snippet': 'definition/snippets/definition_form.html'}
    extra_vars['form_vars'] = dict(extra_vars)
    return toolkit.render('definition/edit.html', extra_vars=extra_vars)


def _save_edit(definition_id, context):
    try:
        data_dict = clean_dict(dict_fns.unflatten(
            tuplize_dict(parse_params(toolkit.request.values))))
        context['message'] = data_dict.get('log_message', '')
        data_dict['id'] = definition_id
        context['allow_partial_update'] = True
        toolkit.get_action('definition_update')(context, data_dict)
        return h.redirect_to('definition_read', definition_id=definition_id)
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized) as e:
        abort(404, toolkit._('Definition not found'))
    except dict_fns.DataError:
        abort(400, _(u'Integrity Error'))
    except toolkit.ValidationError as e:
        errors = e.error_dict
        error_summary = e.error_summary
        return edit(definition_id, data_dict, errors, error_summary)


def delete(definition_id):
    if 'cancel' in toolkit.request.params:
        toolkit.h.redirect_to('definition.edit', definition_id=definition_id)

    context = {'model': model, 'session': model.Session, 'user': toolkit.c.user}

    try:
        toolkit.check_access('definition_delete', context, {'id': definition_id})
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to delete definition %s') % '')

    try:
        if toolkit.request.method == 'POST':
            toolkit.get_action('definition_delete')(context, {'id': definition_id})
            toolkit.h.flash_notice(_('Definition has been deleted.'))
            toolkit.h.redirect_to('definition.search')
        definition_dict = toolkit.get_action('definition_show')(context, {'id': definition_id})
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to delete definition %s') % '')
    except toolkit.ObjectNotFound:
        abort(404, _('Definition not found'))
    except toolkit.ValidationError as e:
        toolkit.h.flash_error(e.error_dict['message'])
        toolkit.h.redirect_to(
            controller='ckanext.definitions.controllers.definition:DefinitionController',
            action='read', id=definition_id
        )
    return toolkit.render_template('definition/confirm_delete.html')
