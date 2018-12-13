import ckan.model.types as _types
from ckan.model import package as _package, package_extra as _package_extra, meta, domain_object
import ckan.model as model
import logging
import datetime
from sqlalchemy import types, Column, Table

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
                 creator_id=None):
        self.label = label
        self.description = description
        self.url = url
        self.enabled = enabled
        self.creator_id = creator_id

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
    def search_by_label(cls, search_term):
        '''Return all definitions whose names contain a given string.

        :param search_term: the string to search for in the definition labels
        :type search_term: string

        :returns: a list of definitions that match the search term
        :rtype: list of ckanext-definition.model.definition.Definition objects

        '''
        query = meta.Session.query(Definition)
        search_term = search_term.strip().lower()
        query = query.filter(Definition.label.contains(search_term))
        query = query.distinct().join(Definition.package_definitions)
        return query

    @classmethod
    def all(cls):
        '''Return all definition

        :param vocab_id_or_name: the id or name of the vocabulary to look in
            (optional, default: None)
        :type vocab_id_or_name: string

        :returns: a list of all definitions that are currently applied to any dataset
        :rtype: list of ckanext-definition.model.definition.Definition objects

        '''

        query = meta.Session.query(Definition)
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
        Column('url', types.UnicodeText),
        Column('enabled', types.Boolean),
        Column('creator_id', types.UnicodeText),
        Column('created_date', types.DateTime,
               default=datetime.datetime.utcnow),
        Column('modified_date', types.DateTime,
               default=datetime.datetime.utcnow),
    )
    meta.mapper(Definition, definition_table)


def create_definition(label, description, url, enabled=True, creator_id=None):
    return Definition(label=label, description=description, url=url,
                      enabled=enabled, creator_id=creator_id)
