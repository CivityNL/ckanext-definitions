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


class DefinitionsPlugin(plugins.SingletonPlugin):
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
            'definition_create': action_create.definition_create,
            'definition_delete': action_delete.definition_delete,
            'data_officer_list': action_get.data_officer_list,
            'data_officer_create': action_create.data_officer_create,
            'data_officer_delete': action_delete.data_officer_delete,
            'add_package_definition': action_create.add_package_definition,
            'definition_update': action_update.definition_update
        }


    #IAuthFunctions
    def get_auth_functions(self):
        return {
            'definition_read': auth_get.definition_read,
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
        return {'is_data_officer': h.is_data_officer}


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

        map.connect('dataset_definition', '/dataset/:id/definition',
                    controller='ckanext.definitions.controllers.definition:DefinitionController',
                    action='dataset_definition')

        # map.connect('definition_list', '/definition',
        #             controller='ckanext.definitions.controllers.definition:DefinitionController',
        #             action='user_preferences')
        #
        # map.connect('definition_read', '/definition/:id',
        #             controller='ckanext.definitions.controllers.definition:DefinitionController',
        #             action='definition_show')
        #
        # map.connect('definition_edit', '/definition/:id/edit',
        #             controller='ckanext.definitions.controllers.definition:DefinitionController',
        #             action='definition_edit')
        # map.connect('/dataset/definition/:package_id',
        #             controller='ckanext.user_preferences.controllers.userpreferencecontroller:UserPreferenceController',
        #             method=['POST'], action='user_preferences_save')

        return map
