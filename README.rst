.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org//ckanext-definitions.svg?branch=master
    :target: https://travis-ci.org//ckanext-definitions

.. image:: https://coveralls.io/repos//ckanext-definitions/badge.svg
  :target: https://coveralls.io/r//ckanext-definitions

.. image:: https://pypip.in/download/ckanext-definitions/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-definitions/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-definitions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-definitions/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-definitions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-definitions/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-definitions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-definitions/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-definitions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-definitions/
    :alt: License

===================
ckanext-definitions
===================

With this plugin user is able to populate a new metadata object 'Definitions' and relate it to one or more datasets.

Enabling this plugin with reveal an additional header tab, from where the user can view, create or modify definitions.

To assign a definition to a dataset, user has to access the edit mode on the dataset of interest, and on the newly revealed tab 'Definitions', search and assign definitions to the dataset.

To view the existing relations between datasets and definition, user has two options:

#. By accessing one definition and getting a list of related datasets
#. By accessing one dataset, navigating to the 'Definitions' tab to retrieve a list of related definitions

------------
Requirements
------------

For the plugin to function properly, additional plugins are requires :

* ckanext-scheming
* ckanext-user_extra

Need to add field "definition" to your dataset schema

-----------------
Config Properties
-----------------

Enable the plugin by including it in the configuration options::

   ckan.plugins = ... definitions ...


Display custom metadata filter::

   ckanext.definitions.search_title_only_filter = {False | True}


Display additional definition metadata::

   ckanext.definitions.show_additional_metadata = {False | True}


--------------------------
Definition object metadata
--------------------------
::

   'label': title of the definition
   'description':  description of the definition
   'url':  (optional) any available reference of the definition
   'enabled': set state of definition
   'discipline': (optional extra) discipline description
   'expertise': (optional extra) expertise description


Boolean config property::

   ckanext.definitions.show_additional_metadata = {False | True}


currently serves for displaying the optional extra fields.


--------------
Internal Notes
--------------

This plugin does not implement scheming capabilities, thus setting up
the definition object metadata is currently hardcoded.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-definitions:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-definitions Python package into your virtual environment::

     pip install ckanext-definitions

3. Add ``definitions`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


----------------------
Dependencies required
----------------------
It is mandatory to use this extension alongside `ckanext-catalog <https://gitlab.onetrail.net/Civity/CKAN/ckanext-catalog>`_ to make use of the universal catalog features and functionality, like catalog email notifications.

---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.definitions.some_setting = some_default_value


------------------------
Development Installation
------------------------

To install ckanext-definitions for development, activate your CKAN virtualenv and
do::

    git clone https://github.com//ckanext-definitions.git
    cd ckanext-definitions
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.definitions --cover-inclusive --cover-erase --cover-tests


