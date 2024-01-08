from .definition import Definition, definition_table
from .definition_package import DefinitionPackage, definition_package_table
import logging as _logging
log = _logging.getLogger(__name__)


def setup():
    for table in [definition_table, definition_package_table]:
        if not table.exists():
            table.create()
            log.debug("Table '{}' was created".format(table.name))
        else:
            log.debug("Table '{}' already exists".format(table.name))
