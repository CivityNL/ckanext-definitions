from ckan.model import DomainObject, meta
from sqlalchemy import types, Column, Table, ForeignKey


definition_package_table = Table(
    'definition_package',
    meta.metadata,
    Column('definition_id', types.UnicodeText, ForeignKey('definition.id'), primary_key=True),
    Column('package_id', types.UnicodeText, ForeignKey('package.id'), primary_key=True),
)


class DefinitionPackage(DomainObject):
    pass


meta.mapper(
    DefinitionPackage,
    definition_package_table
)
