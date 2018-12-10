import ckan
import ckan.lib.dictization
import ckan.model.types as _types
from ckan.model import package as _package, extension as _extension, core, \
    meta, domain_object, activity
import logging
import datetime
from sqlalchemy import types, Column, Table, ForeignKey, DateTime, \
    ForeignKeyConstraint

log = logging.getLogger(__name__)

definition_table = None
package_definition_table = None


def setup():
    if definition_table is None:
        define_definition_table()
        log.debug('Definition table defined in memory')
        create_table(definition_table)
        log.debug('Definition table Created')

    if package_definition_table is None:
        define_package_definition_table()
        log.debug('PackageDefinition table defined in memory')
        create_table(package_definition_table)
        log.debug('PackageDefinition table Created')


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

        log.info('I have been called')
        log.info('self.id = {0}'.format(self.id))

        q = meta.Session.query(_package.Package)
        q = q.join(PackageDefinition)
        q = q.filter_by(definition_id=self.id)
        q = q.filter_by(state='active')
        q = q.order_by(_package.Package.name)

        log.info('q = {0}'.format(q))

        packages = q.all()
        log.info('packages = {0}'.format(packages))

        return packages

    def __repr__(self):
        return '<Definition %s>' % self.label


class PackageDefinition(domain_object.DomainObject):

    @classmethod
    def by_name(self, package_name, definition_label, autoflush=True):
        '''Return the PackageDefinition for the given package and definition
                names/label, or None.

        :param package_name: the name of the package to look for
        :type package_name: string
        :param definition_name: the label of the definition to look for
        :type definition_name: string

        :returns: the PackageDefinition for the given package and definition
                    names/label, or None if there is no PackageTag for those
                    package and definition names/label
        :rtype: ckan.model.tag.PackageTag

        '''
        query = (meta.Session.query(PackageDefinition)
                 .filter(_package.Package.name == package_name)
                 .filter(Definition.label == definition_label))
        query = query.autoflush(autoflush)
        return query.one()[0]


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


def define_package_definition_table():
    global package_definition_table
    package_definition_table = Table(
        'package_definition',
        meta.metadata,
        Column('id', types.UnicodeText, primary_key=True,
               default=_types.make_uuid),
        Column('package_id', types.UnicodeText, ForeignKey('package.id')),
        Column('definition_id', types.UnicodeText,
               ForeignKey('definition.id')),
        Column('revision_id', types.UnicodeText, nullable=False),
        Column('creator_id', types.UnicodeText, nullable=False),
        Column('modifior_id', types.UnicodeText, nullable=False),
        Column('reason', types.UnicodeText, nullable=True),
        Column('state', types.UnicodeText, nullable=False),
        Column('created_date', DateTime, primary_key=True,
               default=datetime.datetime.utcnow),
        ForeignKeyConstraint(['package_id'], ['package.id'],
                             onupdate="CASCADE", ondelete="CASCADE"),
        ForeignKeyConstraint(['definition_id'], ['definition.id'],
                             onupdate="CASCADE", ondelete="CASCADE")
    )
    meta.mapper(PackageDefinition, package_definition_table)


def create_definition(label, description, url, enabled=True, creator_id=None):
    return Definition(label=label, description=description, url=url, enabled=enabled, creator_id=creator_id)


def add_package_definition(session, pkg_dict, modifior_id):
    pkg_model = PackageDefinition()

    pkg_model.package_id = pkg_dict['id']
    pkg_model.definition_id = 'id1'
    pkg_model.revision_id = pkg_dict['revision_id']
    pkg_model.state = pkg_dict['state']
    pkg_model.created_date = datetime.datetime.now()
    pkg_model.creator_id = pkg_dict['creator_user_id']
    pkg_model.modifior_id = modifior_id

    session.add(pkg_model)
    session.commit()
