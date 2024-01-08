# Standard library imports
import logging
# CKAN imports
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import ckan.model as model
# Extension imports
import ckanext.definitions.helpers as h
import ckanext.definitions.logic.action.get as action_get
import ckanext.definitions.logic.action.create as action_create
import ckanext.definitions.logic.action.update as action_update
import ckanext.definitions.logic.action.delete as action_delete
import ckanext.definitions.logic.auth as auth
import ckanext.definitions.logic.auth.get as auth_get
import ckanext.definitions.logic.auth.create as auth_create
import ckanext.definitions.logic.auth.update as auth_update
import ckanext.definitions.logic.auth.delete as auth_delete
import ckanext.definitions.views as views
import ckanext.definitions.command as cli
from ckanext.definitions.model import setup as model_setup, Definition


log = logging.getLogger(__name__)


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
    plugins.implements(plugins.IFacets, inherit=True)

    # IPackageController
    def before_index(self, pkg_dict):
        pkg_dict['definitions'] = [d.id for d in Definition.get_by_package(pkg_dict.get("id"))]
        return pkg_dict

    def after_show(self, context, pkg_dict):
        definitions = Definition.get_by_package(pkg_dict.get("id"))
        pkg_dict["num_definitions"] = len(definitions)
        pkg_dict['definitions'] = [d.dictize(context) for d in definitions]
        return pkg_dict

    def after_search(self, search_results, search_params):
        for item in search_results.get('search_facets', {}).get('definitions', {}).get('items', []):
            definition_id = item['name']
            definition = Definition.get(definition_id)
            item['display_name'] = definition.display_name
        # definitions are not part of the 'validated_data_dict' and will to be added manually
        fields = search_params.get('fl').split(" ") if 'fl' in search_params else []
        if 'validated_data_dict' in fields:
            for result in search_results.get('results', []):
                result = self.after_show({'model': model}, result)
        return search_results

    # IConfigurable
    def configure(self, config):
        model_setup()
        print("configure :: Definition.search")
        for q in ["definition", "definitie", "def"]:
            Definition.search(
                query_string=q, sorting=[("score", "desc"), ("modified_date", "asc")],
                query_fields=[("label", 4)],
                rows=2, start=0, include_disabled=False, exclude=[], fields=["id", "display_name", "score"],
                facet=False, facet_min_count=None, facet_limit=None, facet_fields=None
            )
            Definition.search(
                query_string=q + ':*', sorting=[("score", "desc"), ("modified_date", "asc")],
                query_fields=[("label", 4)],
                rows=2, start=0, include_disabled=False, exclude=[], fields=["id", "display_name", "score"],
                facet=False, facet_min_count=None, facet_limit=None, facet_fields=None
            )




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
            'definition_search': action_get.definition_search,
            'definition_autocomplete': action_get.definition_autocomplete,
            'definition_create': action_create.definition_create,
            'definition_update': action_update.definition_update,
            'definition_delete': action_delete.definition_delete,
            'definition_activity_list': action_get.definition_activity_list,

            'definition_data_officer_list': action_get.definition_data_officer_list,
            'definition_data_officer_create': action_create.definition_data_officer_create,
            'definition_data_officer_delete': action_delete.definition_data_officer_delete,

            'definition_package_relationship_create': action_create.definition_package_relationship_create,
            'definition_package_relationship_delete': action_delete.definition_package_relationship_delete
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'definition_show': auth_get.definition_show,
            'definition_list': auth_get.definition_list,
            'definition_search': auth_get.definition_search,
            'definition_autocomplete': auth_get.definition_autocomplete,
            'definition_create': auth_create.definition_create,
            'definition_update': auth_update.definition_update,
            'definition_delete': auth_delete.definition_delete,
            'definition_activity_list': auth_get.definition_activity_list,

            'definition_data_officer_list': auth_get.definition_data_officer_list,
            'definition_data_officer_manage': auth.definition_data_officer_manage,
            'definition_data_officer_create': auth_create.definition_data_officer_create,
            'definition_data_officer_delete': auth_delete.definition_data_officer_delete,

            'definition_package_relationship_create': auth_create.definition_package_relationship_create,
            'definition_package_relationship_delete': auth_delete.definition_package_relationship_delete
        }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'is_data_officer': h.is_data_officer,
            'package_definition_count': h.package_definition_count,
            'definition_list_choices': h.definition_list_choices,
            'definition_enabled_facet_show': h.definition_enabled_facet_show,
            'definition_user_facet_list_help': h.user_facet_list_help,
            'definition_owner_facet_list_help': h.owner_facet_list_help,
            'definition_search_title_only_filter': h.search_title_only_filter,
            'definition_show_additional_metadata': h.show_additional_metadata
        }

    # IBluePrint
    def get_blueprint(self):
        return views.get_blueprints()

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        log.info("IFacets :: dataset_facets")
        log.info("facets_dict = {}".format(facets_dict))
        facets_dict['definitions'] = toolkit._('Definitions')
        u'''Modify and return the ``facets_dict`` for the dataset search page.

        The ``package_type`` is the type of dataset that these facets apply to.
        Plugins can provide different search facets for different types of
        dataset. See :py:class:`~ckan.plugins.interfaces.IDatasetForm`.

        :param facets_dict: the search facets as currently specified
        :type facets_dict: OrderedDict

        :param package_type: the dataset type that these facets apply to
        :type package_type: string

        :returns: the updated ``facets_dict``
        :rtype: OrderedDict

        '''
        return facets_dict
