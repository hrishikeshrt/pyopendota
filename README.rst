===============
<OPENDOTA/> API
===============


.. image:: https://img.shields.io/pypi/v/pyopendota.svg
        :target: https://pypi.python.org/pypi/pyopendota

.. image:: https://img.shields.io/travis/hrishikeshrt/pyopendota.svg
        :target: https://travis-ci.com/hrishikeshrt/pyopendota

.. image:: https://readthedocs.org/projects/pyopendota/badge/?version=latest
        :target: https://pyopendota.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


A python interface for <OPENDOTA/> API

The :code:`OpenDota` class provided with the package serves as a python
interface for the original OpenDota API in the form of a thin wrapper.
The class assumes some familiarity with the OpenDota API.

All method calls return serializable python objects, as return by the API,
in most cases a dict or a list. Response data is stored as JSON in a local
directory (Default: :code:`~/dota2`), to prevent the load on OpenDota API.


* Free software: MIT license
* Documentation: https://pyopendota.readthedocs.io.


Features
--------

* Transparent wrapper for majority of the API calls
* Ability to authenticate using API key
* In-built and cusomizable limit to protect against frequent API calls
* Local file-based storage for frequent requests


Usage
-----

To use <OPENDOTA/> API in a project::

    import opendota

    # Initialize the API-connection object
    client = opendota.OpenDota()

    # Get common entities
    client.get_matches('match-id')
    client.get_player('player-id')
    client.get_team('team-id')

    # Search Functionality
    players = client.search_player('Dendi')
    teams = client.search_team('Alliance')
    heroes = client.search_hero('Crystal')
    leagues = client.search_league('International')

    # OpenDota API supports arbitrary PostgreSQL query
    # Database Schema
    client.get_schema()           # Lists all tables
    client.get_schema('matches')  # Lists schema for a specific table

    # Arbitrary PostgreSQL Query
    client.explorer("select * from matches where limit 1")


About OpenDota API
------------------

The OpenDota API provides Dota 2 related data including advanced match data
extracted from match replays.

OpenDota API Documentation: https://docs.opendota.com/


Credits
-------

* This package uses data provided by `The OpenDota API`_.

* This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _`The OpenDota API`: https://docs.opendota.com/
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
