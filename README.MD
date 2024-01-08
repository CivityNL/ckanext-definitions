ckanext-definitions
===================

This CKAN extension provides a way to configure and share metadata schemas using a
YAML or JSON schema description. Custom validation and template snippets for editing
and display are supported.

Table of contents:

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Action API Endpoints](#action-api-endpoints)
5. [Running the Tests](#running-the-tests)

Requirements
============

Installation
============

Configuration
=============

Set the schemas you want to use with configuration options:

```ini

# Each of the plugins is optional depending on your use
ckan.plugins = scheming_datasets scheming_groups scheming_organizations

#   module-path:file to schemas being used
scheming.dataset_schemas = ckanext.spatialx:spatialx_schema.yaml
                           ckanext.spatialx:spatialxy_schema.yaml
#   will try to load "spatialx_schema.yaml" and "spatialxy_schema.yaml"
#   as dataset schemas

#   For group and organization schemas (replace myplugin with your custom plugin)
scheming.group_schemas = ckanext.scheming:group_with_bookface.json
                         ckanext.myplugin:/etc/ckan/default/group_with_custom_fields.json
scheming.organization_schemas = ckanext.scheming:org_with_dept_id.json
                                ckanext.myplugin:org_with_custom_fields.json
#
#   URLs may also be used, e.g:
#
# scheming.dataset_schemas = http://example.com/spatialx_schema.yaml

#   Preset files may be included as well. The default preset setting is:
scheming.presets = ckanext.scheming:presets.json

#   The is_fallback setting may be changed as well. Defaults to false:
scheming.dataset_fallback = false
```

Action API Endpoints
====================

The extension adds action endpoints which expose any configured schemas via:
https://github.com/ckan/ckanext-scheming/blob/master/ckanext/scheming/logic.py

## Definitions



Running the Tests
=================


To run the tests:

    pytest --ckan-ini=test.ini ckanext/scheming/tests