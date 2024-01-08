from ckan.plugins import Interface


class IDefinitions(Interface):
    u"""
    Hook into the Definitions view.
    -
    """

    def definitions_after_create(self, context, data_dict):
        pass

    def definitions_after_delete(self, context, data_dict):
        pass

    def definitions_after_update(self, context, data_dict):
        pass

    def definitions_after_show(self, context, def_dict):
        pass

    def definitions_after_search(self, search_results, search_params):
        pass

    def definitions_after_package_relationship_create(self, context, data_dict):
        pass

    def definitions_after_package_relationship_delete(self, context, data_dict):
        pass

    def definitions_after_data_officer_create(self, context, data_dict):
        pass

    def definitions_after_data_officer_delete(self, context, data_dict):
        pass
