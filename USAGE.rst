Usage
=====

Use <OPENDOTA/> API in a project
--------------------------------

.. code-block:: python

    import opendota

    # Initialize the API-connection object
    client = opendota.OpenDota()

Get Common Entities
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client.get_matches('match-id')
    client.get_player('player-id')
    client.get_team('team-id')

Search Functionality
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    players = client.search_player('Dendi')
    teams = client.search_team('Alliance')
    heroes = client.search_hero('Crystal')
    leagues = client.search_league('International')

PostgreSQL Query
^^^^^^^^^^^^^^^^

OpenDota API supports arbitrary PostgreSQL query.

Check Database Schema:

.. code-block:: python

    client.get_schema()           # Lists all tables
    client.get_schema('matches')  # Lists schema for a specific table

Arbitrary PostgreSQL Query:

.. code-block:: python

    client.explorer("select * from matches where limit 1")


Use <OPENDOTA/> API Command Line Interface
------------------------------------------

Information about OpenDota class initialization:

.. code-block:: console

    opendota --help

Information about OpenDota methods:

.. code-block:: console

    opendota - --help

Run methods

.. code-block:: console

    opendota search_team Virtus
    opendota get_match 4080778303

*Powered by :code:`python-fire`*
