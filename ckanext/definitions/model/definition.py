import ckan.model.types as _types
from ckan.model import package as _package, package_extra as _package_extra, \
    meta, domain_object
import ckan.model as model
import logging
import datetime
from sqlalchemy import types, Column, Table, func, or_, and_

log = logging.getLogger(__name__)
definition_table = None


def setup():
    if definition_table is None:
        define_definition_table()
        log.debug('Definition table defined in memory')
        # TODO check if table exists
        create_table(definition_table)
        log.debug('Definition table Created')


def create_table(table=None):
    '''
    Create table
    '''
    if not table.exists():
        table.create()
        log.debug('A table was created')


class Definition(domain_object.DomainObject):

    def __init__(self, label, description='', url='', enabled=True,
                 creator_id=None, definition_id=None):
        self.label = label
        self.description = description
        self.url = url
        self.enabled = enabled
        self.creator_id = creator_id
        self.display_name = label + ' - ' + description
        self.id = definition_id

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
    def search(cls, search_dict, q, enabled=True, sort='asc', limit=20,
               start=0):
        '''Return all definitions which match the criteria.

        :param search_dict: dictionary with key's and values to search.
        :type search_dict: dict

        :returns: a dictionary, with a count of results, and the results
        :rtype: dict, with an count and a list of ckanext-definition.model.definition.Definition objects

        '''

        # Apply the Facets
        query = meta.Session.query(Definition)

        # Show only public Definitions by default
        if enabled:
            query = query.filter(Definition.enabled == enabled)

        for key, value in search_dict.iteritems():
            if key in vars(Definition):
                attribute = getattr(Definition, key)
                query = query.filter(attribute == value)

        # Apply the q
        if q:
            q = q.strip().lower()
            query = query.filter(
                or_(func.lower(Definition.label).contains(q),
                    func.lower(Definition.description).contains(q))
            )

        # TODO remove this from the model
        # Build Facets
        facets = ['creator_id', 'enabled', 'label']
        search_facets = {}
        for key in facets:
            if key in vars(Definition):
                search_facets[key] = {'items': [], 'title': key}
                attribute = getattr(Definition, key)
                for row_value, row_count in query.with_entities(attribute,
                                                                func.count(
                                                                    attribute)).group_by(
                    attribute).all():

                    if isinstance(row_value, (bool, int, float)):
                        row_value = str(row_value)

                    search_facets[key]['items'].append(
                        {'count': row_count, 'display_name': row_value,
                         'name': row_value})

        return {'search_facets': search_facets, 'count': query.count(),
                'results': query.all(), 'query': query}

    @classmethod
    def all(cls, include_disabled):
        '''Return all definition

        :param vocab_id_or_name: the id or name of the vocabulary to look in
            (optional, default: None)
        :type vocab_id_or_name: string

        :returns: a list of all definitions that are currently applied to any dataset
        :rtype: list of ckanext-definition.model.definition.Definition objects

        '''

        query = meta.Session.query(Definition)
        if not include_disabled:
            query = query.filter(Definition.enabled == True)

        return query

    @property
    def packages(self):
        '''Return a list of all packages that have this definition, sorted by name.

        :rtype: list of ckan.model.package.Package objects

        '''
        definition_id = self.id

        q = meta.Session.query(_package.Package)
        q = q.join(_package_extra.PackageExtra)
        q = q.filter(model.PackageExtra.key == 'definition')
        q = q.filter(model.PackageExtra.value.contains(definition_id))
        q = q.filter_by(state='active')
        q = q.order_by(_package.Package.name)
        q = q.with_entities(_package.Package.id)

        packages = q.all()

        return packages

    def __repr__(self):
        return '<Definition %s>' % self.label


def define_definition_table():
    global definition_table
    definition_table = Table(
        'definition',
        meta.metadata,
        Column('id', types.UnicodeText, primary_key=True,
               default=_types.make_uuid),
        Column('label', types.UnicodeText, nullable=False),
        Column('description', types.UnicodeText),
        Column('display_name', types.UnicodeText),
        Column('url', types.UnicodeText),
        Column('enabled', types.Boolean),
        Column('creator_id', types.UnicodeText),
        Column('created_date', types.DateTime,
               default=datetime.datetime.utcnow),
        Column('modified_date', types.DateTime,
               default=datetime.datetime.utcnow),
    )
    meta.mapper(Definition, definition_table)


def create_definition(label, description, url, enabled=True, creator_id=None,
                      definition_id=None):
    return Definition(label=label, description=description, url=url,
                      enabled=enabled, creator_id=creator_id, id=definition_id)
