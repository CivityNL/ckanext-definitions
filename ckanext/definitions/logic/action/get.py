import ckanext.definitions.model.definition as definitions_model
import ckanext.definitions.model_dictize as model_dictize
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import logging
import ckan.lib.dictization as dictization
import ckan.model.misc as misc
import ckan
from six import string_types

NotFound = logic.NotFound
log = logging.getLogger(__name__)
_table_dictize = ckan.lib.dictization.table_dictize


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
        raise NotFound
    result_dict = dictization.table_dictize(result, context)

    return result_dict

# @toolkit.side_effect_free
# def definition_list(context, data_dict):
#     '''
#     Retrieves all the definitions
#     :param context:
#     :return: List of all definitions
#     '''
#     all_definitions = definitions_model.Definition.all()
#     result_dict = []
#
#     for definition in all_definitions:
#         result_dict.append(dictization.table_dictize(definition, context))
#
#     return result_dict



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

    log.info('definition_list ACION ')
    query = data_dict.get('query') or data_dict.get('q')

    if query:
        query = query.strip()
    all_fields = data_dict.get('all_fields', None)

    toolkit.check_access('definition_read', context, data_dict)

    if query:
        definitions, count = _definition_search(context, data_dict)
    else:
        definitions = definitions_model.Definition.all()

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

    terms = data_dict.get('query') or data_dict.get('q') or []
    if isinstance(terms, string_types):
        terms = [terms]
    terms = [t.strip() for t in terms if t.strip()]

    if 'fields' in data_dict:
        log.warning('"fields" parameter is deprecated.  '
                    'Use the "query" parameter instead')

    fields = data_dict.get('fields', {})
    offset = data_dict.get('offset')
    limit = data_dict.get('limit')

    # TODO: should we check for user authentication first?
    q = model.Session.query(definitions_model.Definition)

    # If we're searching free tags, limit results to tags that are
    # currently applied to a package.
    # q = q.distinct().join(model.Tag.package_tags)

    for field, value in fields.items():
        log.info('FIELD -> {0}'.format(field))
        if field in ('tag', 'tags'):
            terms.append(value)

    if not len(terms):
        return [], 0

    for term in terms:
        escaped_term = misc.escape_sql_like_special_characters(
            term, escape='\\')
        q = q.filter(definitions_model.Definition.label.ilike('%' + escaped_term + '%'))

    count = q.count()
    q = q.offset(offset)
    q = q.limit(limit)
    return q.all(), count


def definition_search(context, data_dict):
    '''Return a list of definitions whose labels contain a given string.

    :param query: the string(s) to search for
    :type query: string or list of strings
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
        return [definition.label for definition in matching_definitions]
    else:
        return []


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


