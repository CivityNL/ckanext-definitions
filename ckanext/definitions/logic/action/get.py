from ckanext.definitions.model import Definition
import ckan.logic as _logic
import ckan.plugins.toolkit as toolkit
import logging
import ckan.lib.dictization as dictization
import ckan.model.misc as misc
from ckan.model import User
from sqlalchemy import Boolean, asc, desc
from sqlalchemy.sql.expression import true, or_, and_, select, func
from ckan.lib.dictization.model_dictize import user_dictize, activity_list_dictize
from ckan.logic.schema import default_activity_list_schema, default_pagination_schema
from ckan.logic.action.get import _unpick_search

log = logging.getLogger(__name__)
_table_dictize = dictization.table_dictize


@toolkit.side_effect_free
def definition_show(context, data_dict):
    """
    Retrieves definition details based on the definition 'id'

    :param id: the id of the definition
    :type id: string
    :param include_datasets : include a truncated list of the definition’s datasets (optional, default: ``False``)
    :type include_datasets: bool
    :param include_dataset_count : include the full package_count (optional, default: ``True``)
    :type include_dataset_count: bool
    :param include_extras : include the group’s extra fields (optional, default: ``True``)
    :type include_extras: bool

    :rtype: dictionary
    """

    definition_id = toolkit.get_or_bust(data_dict, 'id')
    definition = Definition.get(definition_id)
    context["definition"] = definition

    dictize_kwargs = {
        'include_datasets': False,
        'include_dataset_count': True,
        'include_extras': True,
    }

    errors = {}
    for kwarg in dictize_kwargs:
        if kwarg in data_dict:
            try:
                dictize_kwargs[kwarg] = toolkit.asbool(data_dict.get(kwarg))
            except ValueError:
                errors[kwarg] = toolkit._('Parameter is not an bool')

    if errors:
        raise toolkit.ValidationError(errors)

    if definition is None:
        raise toolkit.ObjectNotFound

    toolkit.check_access("definition_show", context, data_dict)

    definition_dict = Definition.dictize(definition, context, **dictize_kwargs)

    return definition_dict


@toolkit.side_effect_free
def definition_list(context, data_dict):
    '''Return a list of the id's of the site's definitions.

    :param sort: sorting of the search results. Optional.  Default:
        "label asc" string of field name and sort-order. The allowed fields are
        'label' and 'package_count'
    :type sort: string
    :param limit: the maximum number of results returned (optional)
        Default: ``1000`` when all_fields=false unless set in site's
        configuration ``ckan.group_and_organization_list_max``
        Default: ``25`` when all_fields=true unless set in site's
        configuration ``ckan.group_and_organization_list_all_fields_max``
    :type limit: int
    :param offset: when ``limit`` is given, the offset to start
        returning results from
    :type offset: int
    :param definitions: a list of id's of the definitions to return, if given only
        definitions whose id's are in this list will be returned (optional)
    :type definitions: list of strings
    :param all_fields: return definitions dictionaries instead of just names. Only
        core fields are returned - get some more using the include_* options.
        Returning a list of packages is too expensive, so the `packages`
        property for each group is deprecated, but there is a count of the
        packages in the `package_count` property.
        (optional, default: ``False``)
    :type all_fields: bool
    :param include_dataset_count: if all_fields, include the full package_count
        (optional, default: ``True``)
    :type include_dataset_count: bool
    :param include_extras: if all_fields, include the group extra fields
        (optional, default: ``False``)
    :type include_extras: bool

    :rtype: list of strings
    '''

    toolkit.check_access('definition_list', context, data_dict)

    definitions = data_dict.get('definitions')

    pagination_dict = {}
    limit = data_dict.get('limit')
    if limit:
        pagination_dict['limit'] = data_dict['limit']
    offset = data_dict.get('offset')
    if offset:
        pagination_dict['offset'] = data_dict['offset']
    if pagination_dict:
        pagination_dict, errors = toolkit.navl_validate(data_dict, default_pagination_schema(), context)
        if errors:
            raise toolkit.ValidationError(errors)
    sort = data_dict.get('sort') or toolkit.config.get('ckanext.definitions.default_sort') or 'label'

    all_fields = toolkit.asbool(data_dict.get('all_fields', None))

    if all_fields:
        try:
            max_limit = int(toolkit.config.get('ckanext.definitions.list_all_fields_max', 25))
        except ValueError:
            max_limit = 25
    else:
        try:
            max_limit = int(toolkit.config.get('ckanext.definitions.list_max', 1000))
        except ValueError:
            max_limit = 1000

    if limit is None or int(limit) > max_limit:
        limit = max_limit

    sort_info = _unpick_search(sort, allowed_fields=['label', 'package_count'], total=1)

    query = Definition.all()

    if definitions:
        query = query.filter(Definition.id.in_(definitions))

    if sort_info:
        sort_field = sort_info[0][0]
        sort_direction = sort_info[0][1]
        if sort_field == 'package_count':
            sort_model_field = Definition.package_count
        elif sort_field == 'label':
            sort_model_field = Definition.label

        if sort_direction == 'asc':
            query = query.order_by(asc(sort_model_field))
        else:
            query = query.order_by(desc(sort_model_field))

    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    definitions = query.all()

    if all_fields:
        definition_list = []
        for definition in definitions:
            data_dict['id'] = definition.id
            for key in ('include_extras'):
                if key not in data_dict:
                    data_dict[key] = False

            definition_list.append(toolkit.get_action('definition_show')(context, data_dict))
    else:
        definition_list = [definition.id for definition in definitions]

    return definition_list


def _definition_search(context, data_dict):
    model = context['model']
    user = context['user']

    term = data_dict.get('query') or data_dict.get('q') or []
    include_all = bool(data_dict.get('include_all', False))
    offset = data_dict.get('offset')
    limit = data_dict.get('limit')

    # TODO: should we check for user authentication first?
    q = model.Session.query(Definition)
    if not len(term):
        return [], 0

    escaped_term = misc.escape_sql_like_special_characters(term, escape='\\')
    if include_all:
        q = q.filter(
            or_(
                Definition.label.ilike('%' + escaped_term + '%'),
                Definition.description.ilike('%' + escaped_term + '%'),
                Definition.discipline.ilike('%' + escaped_term + '%'),
                Definition.expertise.ilike('%' + escaped_term + '%'),
            )
        )
    else:
        q = q.filter(Definition.label.ilike('%' + escaped_term + '%'))

    try:
        toolkit.check_access('definition_update', context)
        if 'include_disabled' not in data_dict or not data_dict['include_disabled']:
            q = q.filter(Definition.enabled == true())
    except toolkit.NotAuthorized:
        q = q.filter(Definition.enabled == true())

    count = q.count()
    q = q.offset(offset)
    q = q.limit(limit)
    return q.all(), count


@toolkit.side_effect_free
def definition_search(context, data_dict):
    '''Return a list of definitions whose labels contain a given string.

    :param query: the string(s) to search for
    :type query: string or list of strings
    :param include_disabled: if authorized, returns the definitions that are disabled as well
    :type include_disabled: boolean
    :param limit: the maximum number of tags to return
    :type limit: int
    :param offset: when ``limit`` is given, the offset to start returning tags
        from
    :type offset: int

    :returns: A dictionary with the following keys:

      ``'count'``
        The number of tags in the result.

      ``'results'``
        The list of definitions whose names contain the given string, a list of
        dictionaries.

    :rtype: dictionary

    '''
    definitions, count = _definition_search(context, data_dict)
    return {'count': count,
            'results': [definition.dictize(context) for definition in definitions]}


@toolkit.side_effect_free
def definition_autocomplete(context, data_dict):
    '''Return a list of definition labels that contain a given string.

    :param query: the string to search for
    :type query: string
    :param limit: the maximum number of tags to return
    :type limit: int
    :param offset: when ``limit`` is given, the offset to start returning tags
        from
    :type offset: int

    :rtype: list of strings

    '''
    toolkit.check_access('definition_autocomplete', context, data_dict)
    matching_definitions, count = _definition_search(context, data_dict)
    return [definition.to_dict(context) for definition in matching_definitions]


@toolkit.side_effect_free
def definition_data_officer_list(context, data_dict):
    '''Return a list of the site's user accounts.

    :param q: filter the users returned to those whose names contain a string (optional)
    :type q: string
    :param email: filter the users returned to those whose email match a string (optional) (you must be a sysadmin to
    use this filter)
    :type email: string
    :param order_by: which field to sort the list by (optional, default: ``'display_name'``). Users can be sorted by
    ``'id'``, ``'name'``, ``'fullname'``, ``'display_name'``, ``'created'``, ``'about'``, ``'sysadmin'`` or
    ``'number_created_packages'``.
    :type order_by: string
    :param all_fields: return full user dictionaries instead of just names. (optional, default: ``True``)
    :type all_fields: bool
    :param include_site_user: add site_user to the result (optional, default: ``False``)
    :type include_site_user: bool

    :rtype: list of user dictionaries. User properties include:
      ``number_created_packages`` which excludes datasets which are private or draft state.

    '''
    model = context["model"]

    if data_dict is None:
        data_dict = {}

    order_by_number_created_definitions = False
    if 'order_by' in data_dict and data_dict.get('order_by') == 'number_created_definitions':
        order_by_number_created_definitions = True
        del data_dict['order_by']

    all_fields = toolkit.asbool(data_dict.get('all_fields', True))

    query = toolkit.get_action('user_list')(dict(context, return_query=True), data_dict)

    if all_fields:
        query = query.add_column(
            select([func.count(Definition.id)], and_(
                Definition.creator_id == model.User.id,
                Definition.enabled == True
            )).label('number_created_definitions')
        )

    # add a filter based on if users are 'data officer'
    query = query.filter(
        and_(
            User.plugin_extras is not None,
            User.plugin_extras.has_key("definition"),
            User.plugin_extras["definition"].has_key("data_officer"),
            User.plugin_extras["definition"]["data_officer"].cast(Boolean) == true(),
        )
    )

    if order_by_number_created_definitions:
        query = query.order_by(None).order_by('number_created_definitions', model.User.name)

    users_list = []

    if all_fields:
        for user in query.all():
            result_dict = user_dictize(user[0], context)
            result_dict['number_created_definitions'] = user[user.keys().index('number_created_definitions')]
            users_list.append(result_dict)
    else:
        for user in query.all():
            users_list.append(user[0])

    return users_list


@_logic.validate(default_activity_list_schema)
def definition_activity_list(context, data_dict):
    '''Return a definition's activity stream.

    :param id: the id of the definition
    :type id: string
    :param offset: where to start getting activity items from (optional, default: ``0``)
    :type offset: int
    :param limit: the maximum number of activities to return (optional, default: ``31`` unless set in site's
        configuration ``ckan.activity_list_limit``, upper limit: ``100`` unless set in site's configuration
        ``ckan.activity_list_limit_max``)
    :type limit: int
    :param include_hidden_activity: whether to include 'hidden' activity, which is not shown in the Activity Stream
        page. Hidden activity includes activity done by the site_user, such as harvests, which are not shown in the
        activity stream because they can be too numerous, or activity by other users specified in config option
        `ckan.hide_activity_from_users`. NB Only sysadmins may set include_hidden_activity to true.  (default: false)
    :type include_hidden_activity: bool

    :rtype: list of dictionaries

    '''

    data_dict['include_data'] = False
    include_hidden_activity = data_dict.get('include_hidden_activity', False)
    toolkit.check_access('definition_activity_list', context, data_dict)

    definition_id = data_dict.get('id')
    offset = data_dict.get('offset', 0)
    limit = data_dict['limit']  # defaulted, limited & made an int by schema

    # Convert org_id (could be id or name) into id.
    definition_id = toolkit.get_action('definition_show')(context, {'id': definition_id})['id']

    definition = Definition.get(definition_id)
    activity_objects = definition.activity_list(limit=limit, offset=offset, include_hidden_activity=include_hidden_activity)

    return activity_list_dictize(
        activity_objects, context,
        include_data=data_dict['include_data']
    )
