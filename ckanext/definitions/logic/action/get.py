import ckanext.definitions.model.definition as definitions_model
import ckanext.definitions.model_dictize as model_dictize
import ckan.plugins.toolkit as toolkit
import logging
import ckan.lib.dictization as dictization
import ckan.model.misc as misc
import ast
from sqlalchemy.sql.expression import true, or_


log = logging.getLogger(__name__)
_table_dictize = dictization.table_dictize


@toolkit.side_effect_free
def definition_show(context, data_dict):
    '''
    Retrieves definition details based on the definition 'id'
    :param context:
    :param data_dict: contains the definition 'id'
    :return: details of definition
    '''
    definition_id = data_dict.get('id')
    result = definitions_model.Definition.get(definition_id)
    if result is None:
        raise toolkit.ObjectNotFound
    result_dict = dictization.table_dictize(result, context)

    return result_dict


@toolkit.side_effect_free
def definition_list(context, data_dict):
    '''Return a list of the site's tags.

    By default only free tags (tags that don't belong to a vocabulary) are
    returned. If the ``vocabulary_id`` argument is given then only tags
    belonging to that vocabulary will be returned instead.

    :param query: a tag name query to search for, if given only tags whose
        names contain this string will be returned (optional)
    :type query: string
    :param vocabulary_id: the id or name of a vocabulary, if give only tags
        that belong to this vocabulary will be returned (optional)
    :type vocabulary_id: string
    :param all_fields: return full tag dictionaries instead of just names
        (optional, default: ``False``)
    :type all_fields: bool

    :rtype: list of dictionaries

    '''

    query = data_dict.get('query') or data_dict.get('q')

    if query:
        query = query.strip()
    all_fields = data_dict.get('all_fields', None)

    toolkit.check_access('definition_read', context, data_dict)

    if query:
        definitions, count = _definition_search(context, data_dict)
    else:
        try:
            toolkit.check_access('definition_update', context, data_dict)
            definitions = definitions_model.Definition.all(include_disabled=True)
        except toolkit.NotAuthorized:
            definitions = definitions_model.Definition.all(include_disabled=False)

    if definitions:
        if all_fields:
            result = model_dictize.definition_list_dictize(definitions, context)
        else:
            result = [definition.id for definition in definitions]
    else:
        result = []

    return result


def _definition_search(context, data_dict):
    model = context['model']
    user = context['user']

    term = data_dict.get('query') or data_dict.get('q') or []
    include_all = bool(data_dict.get('include_all', False))
    offset = data_dict.get('offset')
    limit = data_dict.get('limit')

    # TODO: should we check for user authentication first?
    q = model.Session.query(definitions_model.Definition)
    if not len(term):
        return [], 0

    escaped_term = misc.escape_sql_like_special_characters(term, escape='\\')
    if include_all:
        q = q.filter(
            or_(
                definitions_model.Definition.label.ilike('%' + escaped_term + '%'),
                definitions_model.Definition.description.ilike('%' + escaped_term + '%'),
                definitions_model.Definition.discipline.ilike('%' + escaped_term + '%'),
                definitions_model.Definition.expertise.ilike('%' + escaped_term + '%'),
            )
        )
    else:
        q = q.filter(definitions_model.Definition.label.ilike('%' + escaped_term + '%'))

    try:
        toolkit.check_access('definition_update', context)
        if 'include_disabled' not in data_dict or not data_dict['include_disabled']:
            q = q.filter(definitions_model.Definition.enabled == true())
    except toolkit.NotAuthorized:
        q = q.filter(definitions_model.Definition.enabled == true())

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
            'results': [_table_dictize(definition, context) for definition in definitions]}


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
    if matching_definitions:

        return [dictization.table_dictize(definition, context) for definition in matching_definitions]
    else:
        return []


@toolkit.side_effect_free
def search_packages_by_definition(context, data_dict):
    '''Return a list of packages associated with the definition.

    :param definition_id: a tag name query to search for, if given only tags whose
    :type definition_id: string
    :param all_fields: return full tag dictionaries instead of just names
    :type all_fields: bool

    :rtype: list of package dictionaries

    '''

    definition_id = data_dict.get('definition_id')
    all_fields = data_dict.get('all_fields', None)

    toolkit.check_access('definition_read', context, data_dict)
    definition = definitions_model.Definition.get(definition_id=definition_id)
    packages = definition.packages

    if packages:
        if all_fields:
            result = [toolkit.get_action('package_show')(context, {'id': package}) for package in packages]
        else:
            result = [package.name for package in packages]
    else:
        result = []

    return result


@toolkit.side_effect_free
def search_definitions_by_package(context, data_dict):
    '''Return a list of definitions associated with the package.

    :param package_id: a tag name query to search for, if given only tags whose
    :type package_id: string

    :rtype: list of dictionaries

    '''

    package_id = data_dict.get('package_id')
    pkg_dict = toolkit.get_action('package_show')(context, {'id': package_id})

    try:
        definitions = toolkit.get_or_bust(pkg_dict, ['definition'])
    except toolkit.ValidationError:
        return []

    if definitions:
        definitions = ast.literal_eval(definitions)
    else:
        definitions = list()

    result = []

    for definition in definitions:
        log.info('definition = {0}'.format(definition))
        try:
            result.append(toolkit.get_action('definition_show')(context, {'id': definition}))
        except toolkit.ObjectNotFound:
            pass
    ordered_result = sorted(result, key=lambda k: k['label'])

    return ordered_result


##############################################################
##############################################################
#  Data Officer
##############################################################
##############################################################

@toolkit.side_effect_free
def data_officer_list(context, data_dict):
    '''
    Retrieves all users which are data officers
    :param context:
    :param include_all_user_info:
    :return: List of all data officers
    '''
    result = []
    user_list = toolkit.get_action('user_list')(context, {})

    for user in user_list:
        user_extras = toolkit.get_action('user_extra_show')(context, {"user_id": user['id']})['extras']
        for extra_dict in user_extras:
            if extra_dict['key'] == 'Data Officer' and extra_dict['value'] == 'True':
                if 'include_all_user_info' in data_dict and data_dict['include_all_user_info']:
                    result.append(user)
                else:
                    user_dict = {
                        "id":user['id'],
                        "name": user['name'],
                        "display_name": user['display_name']
                    }
                    result.append(user_dict)
                break

    return result

