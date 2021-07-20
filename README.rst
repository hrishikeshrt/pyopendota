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




A thin wrapper for <OPENDOTA/> API


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

    # Database Schema
    client.get_schema()
    client.get_schema('matches')

    # Arbitrary Query
    client.explorer("select * from matches where limit 1")


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
