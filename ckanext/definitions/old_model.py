import sqlalchemy.orm as orm
import sqlalchemy.types as types
import logging
import datetime
from ckan.model.domain_object import DomainObject
from ckan.model import meta, extension
import ckan.model.types as _types

from sqlalchemy.schema import Table, Column, ForeignKey, CreateTable, Index

mapper = orm.mapper
log = logging.getLogger(__name__)

definition_table = None


def setup():
    if definition_table is None:
        define_definition_table()
        log.debug('Definition table defined in memory')

    create_table()


class Definition(DomainObject):
    '''
    Definition information
    '''

    def __init__(self, label, description, url, enabled, creator_id, definition_id=None, created_date=None, modified_date=None):
        self.id = definition_id
        self.label = label
        self.description = description
        self.url = url
        self.enabled = enabled
        self.creator_id = creator_id
        self.created_date = created_date
        self.modified_date = modified_date


    @classmethod
    def get(cls, definition_id):
        query = meta.Session.query(Definition)
        return query.filter_by(id=definition_id).first()

    @classmethod
    def get_by_label(cls, label):
        query = meta.Session.query(Definition).filter_by(label=label)
        result = query.all()
        return result

    @classmethod
    def get_all(cls):
        query = meta.Session.query(Definition)
        return query.all()

    @classmethod
    def check_exists(cls):
        return definition_table.exists()


def define_definition_table():
    global definition_table
    definition_table = Table('definition', meta.metadata,
                             Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
                             Column('label', types.UnicodeText),
                             Column('description', types.UnicodeText),
                             Column('url', types.UnicodeText),
                             Column('enabled', types.Boolean),
                             # Column('creator_id', types.UnicodeText, ForeignKey('user.id')),
                             Column('creator_id', types.UnicodeText),
                             Column('created_date', types.DateTime, default=datetime.datetime.utcnow),
                             Column('modified_date', types.DateTime, default=datetime.datetime.utcnow),
                              )
    mapper(Definition, definition_table, extension=[extension.PluginMapperExtension(), ])


def _create_definition(label, description, url, enabled=True, creator_id=None):
    return Definition(label=label, description=description, url=url, enabled=enabled, creator_id=creator_id)


def create_table():
    '''
    Create definition table
    '''
    if not definition_table.exists():
        definition_table.create()
        log.debug('Definition table created')


def delete_table():
    '''
    Delete information from definition table
    '''
    print 'Definition trying to delete table...'
    if definition_table.exists():
        print 'Definition delete table...'
        definition_table.delete()
        log.debug('Definition table deleted')
        print 'DONE Definition delete table...'


def drop_table():
    '''
    Drop definition table
    '''
    print 'User Extra trying to drop table...'
    if definition_table.exists():
        print 'User Extra drop table...'
        definition_table.drop()
        log.debug('Validation Token table dropped')
        print 'DONE User Extra drop table...'
