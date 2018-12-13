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

