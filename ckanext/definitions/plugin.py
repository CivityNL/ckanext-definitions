import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.definitions.model.definition as definition_model
import ckanext.definitions.logic.action.get as definition_get
import ckanext.definitions.logic.action.create as definition_create
import ckanext.definitions.logic.action.update as definition_update
import ckanext.definitions.logic.action.delete as definition_delete


class DefinitionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
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
            'definition_show': definition_get.definition_show,
            'definition_list': definition_get.definition_list,
            'definition_create': definition_create.definition_create,
            'definition_delete': definition_delete.definition_delete,
            'add_package_definition': definition_create.add_package_definition,
            'definition_update': definition_update.definition_update
        }

    #IRoutes
    def before_map(self, map):

        map.connect('definition_search', '/definition',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='search')


        map.connect('definition_new', '/definition/new',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='new')

        map.connect('definition_edit', '/definition/edit/{definition_id}',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='edit')

        map.connect('definition_delete', '/definition/delete/{definition_id}',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='delete')

        map.connect('definition_read', '/definition/{definition_id}',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='read')



        map.connect('dataset_definition', '/dataset/:id/definition',
                    controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
                    action='dataset_definition')

        # map.connect('definition_list', '/definition',
        #             controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
        #             action='user_preferences')
        #
        # map.connect('definition_read', '/definition/:id',
        #             controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
        #             action='definition_show')
        #
        # map.connect('definition_edit', '/definition/:id/edit',
        #             controller='ckanext.definitions.controllers.definitioncontroller:DefinitionController',
        #             action='definition_edit')
        # map.connect('/dataset/definition/:package_id',
        #             controller='ckanext.user_preferences.controllers.userpreferencecontroller:UserPreferenceController',
        #             method=['POST'], action='user_preferences_save')

        return map
