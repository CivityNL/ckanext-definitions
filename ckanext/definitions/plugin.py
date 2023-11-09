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
import ckanext.definitions.views as views
import ckanext.definitions.command as cli
from ckanext.definitions.model.definition import Definition


class DefinitionsPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)

    # IPackageController
    def before_index(self, pkg_dict):
        pkg_dict['definitions'] = [d.id for d in Definition.get_by_package(pkg_dict.get("id"))]
        return pkg_dict

    # IConfigurable
    def configure(self, config):
        definition_model.setup()

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'definitions')


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
                'package_definition_count': h.package_definition_count,
                'definition_list_choices': h.definition_list_choices,
                'definition_enabled_facet_show': h.definition_enabled_facet_show,
                'definition_user_facet_list_help': h.user_facet_list_help,
                'definition_owner_facet_list_help': h.owner_facet_list_help,
                'definition_search_title_only_filter': h.search_title_only_filter,
                'definition_show_additional_metadata': h.show_additional_metadata
                }

    #IBluePrint
    def get_blueprint(self):
        return views.get_blueprints()


    #IClick
    def get_commands(self):
        return cli.get_commands()
