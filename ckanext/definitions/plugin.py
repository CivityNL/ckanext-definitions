import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.definitions.helpers as h
import ckanext.definitions.model.definition as definition_model
import ckanext.definitions.logic.action.get as action_get
import ckanext.definitions.logic.action.create as action_create
import ckanext.definitions.logic.action.update as action_update
import ckanext.definitions.logic.action.delete as action_delete
import ckanext.definitions.logic.auth.get as auth_get
import ckanext.definitions.logic.auth.create as auth_create
import ckanext.definitions.logic.auth.update as auth_update
import ckanext.definitions.logic.auth.delete as auth_delete
from ckan.lib.plugins import DefaultTranslation


class DefinitionsPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurable
    def configure(self, config):
        definition_model.setup()

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'definitions')


    # IActions
    def get_actions(self):
        return {
            'definition_show': action_get.definition_show,
            'definition_list': action_get.definition_list,
            'definition_autocomplete': action_get.definition_autocomplete,
            'definition_create': action_create.definition_create,
            'definition_update': action_update.definition_update,
            'definition_delete': action_delete.definition_delete,
            'search_packages_by_definition': action_get.search_packages_by_definition,
            'search_definitions_by_package': action_get.search_definitions_by_package,
            'data_officer_list': action_get.data_officer_list,
            'data_officer_create': action_create.data_officer_create,
            'data_officer_delete': action_delete.data_officer_delete,
            'package_definition_create': action_create.package_definition_create,
            'package_definition_delete': action_delete.package_definition_delete

        }


    #IAuthFunctions
    def get_auth_functions(self):
        return {
            'definition_read': auth_get.definition_read,
            'definition_autocomplete': auth_get.definition_autocomplete,
            'definition_create': auth_create.definition_create,
            'definition_update': auth_update.definition_update,
            'definition_delete': auth_delete.definition_delete,
            'data_officer_read': auth_get.data_officer_read,
            'data_officer_manage': auth_update.data_officer_manage,
            'data_officer_create': auth_create.data_officer_create,
            'data_officer_delete': auth_delete.data_officer_delete
        }


    # ITemplateHelpers
    def get_helpers(self):
        return {'is_data_officer': h.is_data_officer,
                'definition_list_choices': h.definition_list_choices,
                'definition_enabled_facet_show': h.definition_enabled_facet_show,
                'definition_maker_facet_list_help': h.maker_facet_list_help,
                'definition_owner_facet_list_help': h.owner_facet_list_help
                }

    #IRoutes
    def before_map(self, map):

        # Definitions
        map.connect('definition_search', '/definition',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='search')
        map.connect('definition_new', '/definition/new',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='new')
        map.connect('definition_edit', '/definition/edit/{definition_id}',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='edit')
        map.connect('definition_delete', '/definition/delete/{definition_id}',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='delete')
        map.connect('definition_read', '/definition/{definition_id}',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='read')

        # Data Officer
        map.connect('data_officer_index', '/data_officer',
                    controller='ckanext.definitions.controllers.data_officer:DataOfficerController',
                    action='index')
        map.connect('data_officer_new', '/data_officer/new',
                    controller='ckanext.definitions.controllers.data_officer:DataOfficerController',
                    action='new')
        map.connect('data_officer_edit', '/data_officer/edit',
                    controller='ckanext.definitions.controllers.data_officer:DataOfficerController',
                    action='edit')
        map.connect('data_officer_delete', '/data_officer/delete/{user_id}',
                    controller='ckanext.definitions.controllers.data_officer:DataOfficerController',
                    action='delete')


        # Package Definitions
        map.connect('dataset_definition_read', '/dataset/definitions/:package_id',
                    controller='ckanext.definitions.controllers.package_definition:PackageDefinitionController',
                    action='read')
        map.connect('dataset_definition_edit', '/dataset/definitions/:package_id/edit',
                    controller='ckanext.definitions.controllers.package_definition:PackageDefinitionController',
                    action='edit')
        map.connect('dataset_definition_new', '/dataset/definitions/:package_id/new',
                    controller='ckanext.definitions.controllers.package_definition:PackageDefinitionController',
                    action='new')
        map.connect('dataset_definition_delete', '/dataset/definitions/{package_id}/delete/{definition_id}',
                    controller='ckanext.definitions.controllers.package_definition:PackageDefinitionController',
                    action='delete')


        return map
