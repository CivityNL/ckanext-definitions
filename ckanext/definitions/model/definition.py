import ckan.model.types as _types
from datetime import datetime
import ckanext.definitions.helpers as definition_helpers
from ckan.model import DomainObject, meta, Package as _Package, Activity as _Activity, User as _User
from ckan.model.activity import _filter_activitites_from_users, _activities_at_offset
from sqlalchemy import types, Column, Table, func, or_, ForeignKey, orm, true, select
from ckanext.definitions.model.definition_package import definition_package_table as _definition_package_table
from ckan.lib import dictization
import sqlalchemy
from sqlalchemy.dialects.postgresql import TSVECTOR


definition_table = Table(
    'definition', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column('label', types.UnicodeText, nullable=False),
    Column('description', types.UnicodeText),
    Column('url', types.UnicodeText),
    Column('enabled', types.Boolean, default=True),
    Column('creator_id', types.UnicodeText, ForeignKey('user.id', ondelete='SET NULL')),
    Column('discipline', types.UnicodeText),
    Column('expertise', types.UnicodeText),
    Column('created_date', types.DateTime, default=datetime.utcnow),
    Column('modified_date', types.DateTime, default=datetime.utcnow),
)

DEFAULT_FACETS = ['creator_id', 'enabled', 'label']
ADDITIONAL_FIELDS = ['discipline', 'expertise']

definition_fields = ['id', 'label', 'description', 'url', 'enabled', 'disciple', 'expertise']

class Definition(DomainObject):


    def __init__(self, label, description='', url='', enabled=True,
                 creator_id=None, definition_id=None,
                 discipline=None, expertise=None):
        self.label = label
        self.description = description
        self.url = url
        self.enabled = enabled
        self.creator_id = creator_id
        self.id = definition_id

        # Additional customer metadata
        self.discipline = discipline
        self.expertise = expertise

    # not stateful so same as purge
    def delete(self):
        self.purge()

    @classmethod
    def get(cls, definition_id, autoflush=True):
        '''Return the definition with the given id, or None.

        :param autoflush:
        :type autoflush: boolean

        :param definition_id: the id of the definition to return
        :type definition_id: string

        :returns: the definition with the given id, or None if there is no
            definition with that id
        :rtype: ckanext-definition.model.definition.Definition

        '''
        query = meta.Session.query(Definition).filter(
            Definition.id == definition_id)
        query = query.autoflush(autoflush)
        definition = query.first()

        return definition

    @classmethod
    def get_by_package(cls, package_id, autoflush=True, include_disabled=False):
        query = meta.Session.query(Definition).\
            filter(Definition.packages_all.any(id=package_id))
        if not include_disabled:
            query = query.filter(Definition.enabled == True)
        query = query.autoflush(autoflush)
        definitions = query.all()
        return definitions

    @classmethod
    def get_by_creator_id(cls, creator_id, autoflush=True, include_disabled=False):
        query = meta.Session.query(Definition).\
            filter(Definition.creator_id == creator_id)
        if not include_disabled:
            query = query.filter(Definition.enabled == True)
        query = query.autoflush(autoflush)
        definitions = query.all()
        return definitions


    # @classmethod
    # def search(cls, search_dict, q, search_title_only, enabled=True, sort='asc', limit=20, start=0):
    #     '''Return all definitions which match the criteria.
    #
    #     :param search_dict: dictionary with key's and values to search.
    #     :type search_dict: dict
    #     :param q: search keyword.
    #     :type q: str
    #     :param search_title_only: search only in the title.
    #     :type search_title_only: str
    #
    #     :returns: a dictionary, with a count of results, and the results
    #     :rtype: dict, with an count and a list of ckanext-definition.model.definition.Definition objects
    #
    #     '''
    #     # Apply the Facets
    #     query = meta.Session.query(Definition)
    #
    #     # Show only public Definitions by default
    #     if enabled:
    #         query = query.filter(Definition.enabled == enabled)
    #
    #     for key, value in search_dict.items():
    #         if key in vars(Definition):
    #             attribute = getattr(Definition, key)
    #             query = query.filter(attribute == value)
    #
    #     # Apply the q
    #     if q:
    #         q = q.strip().lower()
    #         if search_title_only == "false":
    #             query = query.filter(
    #                 or_(
    #                     func.lower(Definition.label).contains(q),
    #                     func.lower(Definition.description).contains(q),
    #                     func.lower(Definition.discipline).contains(q),
    #                     func.lower(Definition.expertise).contains(q))
    #             )
    #         else:
    #             query = query.filter(func.lower(Definition.label).contains(q))
    #
    #
    #     # TODO remove this from the model
    #     # Build Facets
    #     facets = get_facets() # include additional metadata in search facets
    #     search_facets = {}
    #     for key in facets:
    #         if key in vars(Definition):
    #             search_facets[key] = {'items': [], 'title': key}
    #             attribute = getattr(Definition, key)
    #             for row_value, row_count in query.with_entities(attribute, func.count(attribute)).group_by(attribute).all():
    #
    #                 if isinstance(row_value, (bool, int, float)):
    #                     row_value = str(row_value)
    #
    #                 search_facets[key]['items'].append(
    #                     {'count': row_count, 'display_name': row_value,
    #                      'name': row_value})
    #
    #     return {'search_facets': search_facets, 'count': query.count(),
    #             'results': query.all(), 'query': query}

    @classmethod
    def all(cls, include_disabled=False):
        '''Return all definitions

        :param include_disabled: should disabled definitions be included in the result
            (optional, default: False)
        :type include_disabled: boolean

        :returns: a list of all definitions that are currently applied to any dataset
        :rtype: list of ckanext-definition.model.definition.Definition objects

        '''

        query = meta.Session.query(Definition)
        if not include_disabled:
            query = query.filter(Definition.enabled == True)

        return query

    @property
    def packages(self):
        return [package.id for package in self.packages_all]

    @property
    def package_count(self):
        return len(self.packages_all)


    @property
    def display_name(self):
        return self.label + ' - ' + self.description


    def to_dict(self, context):
        result = dictization.table_dictize(self, context)
        result['display_name'] = self.display_name
        result['packages'] = self.packages
        return result


    def dictize(self, context, include_extras=True, include_datasets=False, include_dataset_count=True):

        result_dict = dictization.table_dictize(self, context)

        result_dict['display_name'] = self.display_name

        if include_dataset_count:
            result_dict['dataset_count'] = self.package_count

        if include_datasets:
            result_dict['datasets'] = definition_helpers.get_packages_for_definition(context, self)

        return result_dict


    @classmethod
    def list_dictize(cls, obj_list, context, sort_key=lambda x: x['display_name'], reverse=False,
                       include_dataset_count=True, include_extras=False):
        dictize_context = dict(context.items())
        dictize_options = {
            'include_dataset_count': include_dataset_count,
            'include_extras': include_extras
            }
        definition_list = [obj.dictize(obj, dictize_context, **dictize_options) for obj in obj_list]
        return sorted(definition_list, key=sort_key, reverse=reverse)


    def activity_list(self, limit, offset, include_hidden_activity):
        import ckan.model as model
        q = model.Session.query(model.Activity).filter_by(object_id=self.id)
        if not include_hidden_activity:
            q = _filter_activitites_from_users(q)
        return _activities_at_offset(q, limit, offset)


    def activity_stream_item(self, activity_type, user_id):
        import ckan.model
        import ckan.logic

        assert activity_type in ("new", "changed"), (
            str(activity_type))

        try:
            # We save the entire rendered package dict so we can support
            # viewing the past packages from the activity feed.
            dictized_definition = ckan.logic.get_action('definition_show')({
                'model': ckan.model,
                'session': ckan.model.Session,
                'for_view': False,  # avoid ckanext-multilingual translating it
                'ignore_auth': True
            }, {
                'id': self.id
            })
        except ckan.logic.NotFound:
            # This happens if this package is being purged and therefore has no
            # current revision.
            # TODO: Purge all related activity stream items when a model object
            # is purged.
            return None

        actor = meta.Session.query(_User).get(user_id)

        return _Activity(
            user_id,
            self.id,
            "%s definition" % activity_type,
            {
                'definition': dictized_definition,
                # We keep the acting user name around so that actions can be
                # properly displayed even if the user is deleted in the future.
                'actor': actor.name if actor else None
            }
        )


    @classmethod
    def search(cls, query_string: str, sorting: list[tuple[str, str]], query_fields: list[tuple[str, float]],
               rows: int, start: int, include_disabled: bool, exclude: list[str], fields: list[str],
               facet: bool, facet_min_count: int, facet_limit: int, facet_fields: list[str]) -> (list, dict):
        """
        @param query_string: the search query. Optional
        @param sorting: sorting of the search results. Optional. Default: 'score desc, metadata_modified desc'
        @param query_fields: list of fieldnames to query, might include weight e.g. [label^3]

        @param rows: number of results to return
        @param start: the offset in the complete result for where the set of returned definitions should begin
        @param include_disabled: if True, disabled definitions will be included in the results
        @param exclude: list of definitions to exclude from the results
        @param fields: list of fieldnames to return in the results

        @param facet: whether to enable faceted results.
        @param facet_min_count: the minimum counts for facet fields should be included in the results.
        @param facet_limit: the maximum number of values the facet fields return. A negative value means unlimited.
                            This can be set instance-wide with the ckanext.definitions.facets.limit config option.
                            Default is 50.
        @param facet_fields: the fields to facet upon. Default empty. If empty, no facet information is returned.
        """
        print("Definition :: search")
        print("Definition :: search :: query_string = {}".format(query_string))
        print("Definition :: search :: sorting = {}".format(sorting))
        print("Definition :: search :: query_fields = {}".format(query_fields))
        print("Definition :: search :: rows = {}".format(rows))
        print("Definition :: search :: start = {}".format(start))
        # print("Definition :: search :: include_disabled = {}".format(include_disabled))
        # print("Definition :: search :: exclude = {}".format(exclude))
        # print("Definition :: search :: fields = {}".format(fields))
        # print("Definition :: search :: facet = {}".format(facet))
        # print("Definition :: search :: facet_min_count = {}".format(facet_min_count))
        # print("Definition :: search :: facet_limit = {}".format(facet_limit))
        # print("Definition :: search :: facet_fields = {}".format(facet_fields))
        query_dict = {}

        query_language = 'simple'
        document_language = 'simple'

        # query = func.websearch_to_tsquery(query_language, query_string)
        query = func.to_tsquery(query_language, query_string)

        document = None
        for field, weight in query_fields:
            tsvector = func.to_tsvector(document_language, func.coalesce(getattr(Definition, field), ''))
            # tsvector = func.edge_gram_tsvector(document_language, func.coalesce(getattr(Definition, field), ''))
            if document is None:
                document = tsvector
            else:
                document = document.bool_op("||")(tsvector)

        score = func.ts_rank_cd(document, query)

        sql = meta.Session.query(cls, score, query, document, query.bool_op("@@")(document))
        if document is not None:
            sql = sql.filter(query.bool_op("@@")(document))
        if not include_disabled:
            sql = sql.filter(Definition.enabled == true())
        if exclude:
            sql = sql.filter(Definition.id.not_in(exclude))


        if facet:
            # do something related to facets
            pass

        for sort_field, sort_direction in sorting:
            if sort_field == 'score':
                sql = sql.order_by(getattr(sqlalchemy, sort_direction)(score))
            else:
                sql = sql.order_by(getattr(sqlalchemy, sort_direction)(getattr(Definition, sort_field)))

        print("Definition :: sql = {}".format(sql))
        print("Definition :: search_results = {}".format(sql.count()))

        [print(result) for result in sql.all()]

        sql = sql.limit(rows).offset(start)

        search_results = [result[0].id for result in sql.all()]

        print("Definition :: search_results = {}".format(search_results))
        return search_results, {}


    def __repr__(self):
        return '<Definition %s>' % self.label


def create_definition(label, description, url, enabled=True, creator_id=None,
                      discipline=None, expertise=None):
    return Definition(
        label=label,
        description=description,
        url=url,
        enabled=enabled,
        creator_id=creator_id,
        discipline=discipline,
        expertise=expertise
    )


def get_facets():
    facets = DEFAULT_FACETS
    show_additional_facets = definition_helpers.show_additional_metadata()
    if show_additional_facets:
        facets = facets + ADDITIONAL_FIELDS

    return facets


meta.mapper(Definition, definition_table, properties={
    "packages_all": orm.relationship(_Package, secondary=_definition_package_table)
})
