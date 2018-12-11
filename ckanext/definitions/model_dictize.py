# encoding: utf-8

'''
These dictize functions generally take a domain object (such as Package) and
convert it to a dictionary, including related objects (e.g. for Package it
includes PackageTags, PackageExtras, PackageGroup etc).

The basic recipe is to call:

    dictized = ckan.lib.dictization.table_dictize(domain_object)

which builds the dictionary by iterating over the table columns.
'''
import datetime
import urlparse

from ckan.common import config
from sqlalchemy.sql import select

import ckan.logic as logic
import ckan.plugins as plugins
import ckan.lib.helpers as h
import ckan.lib.dictization as d
import ckan.authz as authz
import ckan.lib.search as search
import ckan.lib.munge as munge


def definition_list_dictize(definition_list, context):

    result_list = []
    for definition in definition_list:
        if context.get('with_capacity'):
            definition, capacity = definition
            dictized = d.table_dictize(definition, context, capacity=capacity)
        else:
            dictized = d.table_dictize(definition, context)

        # Add display_names to tag dicts. At first a tag's display_name is just
        # the same as its name, but the display_name might get changed later
        # (e.g.  translated into another language by the multilingual
        # extension).
        assert not dictized.has_key('display_name')
        dictized['display_name'] = dictized['label']

        result_list.append(dictized)

    return result_list


def definition_dictize(definition, context, include_datasets=True):
    definition_dict = d.table_dictize(definition, context)

    if include_datasets:
        query = search.PackageSearchQuery()

        definition_query = u'+capacity:public '
        tag_query += u'+definition:"{0}"'.format(definition.id)

        q = {'q': definition_query, 'fl': 'data_dict', 'wt': 'json', 'rows': 1000}

        package_dicts = [h.json.loads(result['data_dict'])
                         for result in query.run(q)['results']]

    # Add display_names to tags. At first a tag's display_name is just the
    # same as its name, but the display_name might get changed later (e.g.
    # translated into another language by the multilingual extension).
    assert 'display_name' not in definition_dict
    definition_dict['display_name'] = definition_dict['label']

    if context.get('for_view'):
        if include_datasets:
            definition_dict['packages'] = []
            for package_dict in package_dicts:
                for item in plugins.PluginImplementations(plugins.IPackageController):
                    package_dict = item.before_view(package_dict)
                    definition_dict['packages'].append(package_dict)
    else:
        if include_datasets:
            definition_dict['packages'] = package_dicts

    return definition_dict