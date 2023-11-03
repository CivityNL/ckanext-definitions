from flask import Blueprint
import ckanext.definitions.controllers.definition as DefinitionController
import ckanext.definitions.controllers.data_officer as DataOfficerController
import ckanext.definitions.controllers.package_definition as PackageDefinitionController

definition = Blueprint('definition', __name__, url_prefix='/definition')
definition.add_url_rule('/', view_func=DefinitionController.search)
definition.add_url_rule('/new', view_func=DefinitionController.new)
definition.add_url_rule('/edit/<definition_id>', view_func=DefinitionController.edit)
definition.add_url_rule('/delete/<definition_id>', view_func=DefinitionController.delete)
definition.add_url_rule('/<definition_id>', view_func=DefinitionController.read)

data_officer = Blueprint('data_officer', __name__, url_prefix='/data_officer')
data_officer.add_url_rule('/', view_func=DataOfficerController.index, methods=['GET'])
data_officer.add_url_rule('/new', view_func=DataOfficerController.new, methods=['GET', 'POST'])
data_officer.add_url_rule('/edit', view_func=DataOfficerController.edit, methods=['GET', 'POST'])
data_officer.add_url_rule('/delete/<user_id>', view_func=DataOfficerController.delete, methods=['GET', 'POST'])

dataset_definition = Blueprint('dataset_definition', __name__, url_prefix='/dataset/definitions')
dataset_definition.add_url_rule('/<package_id>', view_func=PackageDefinitionController.read)
dataset_definition.add_url_rule('/<package_id>/edit', view_func=PackageDefinitionController.edit)
dataset_definition.add_url_rule('/<package_id>/new', view_func=PackageDefinitionController.new)
dataset_definition.add_url_rule('/<package_id>/delete/<definition_id>', view_func=PackageDefinitionController.delete)


def get_blueprints():
    return [definition, data_officer, dataset_definition]
