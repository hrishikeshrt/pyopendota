=====
Usage
=====

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


Use <OPENDOTA/> API command line interface (Powered by `python-fire`)::

    # Information about OpenDota class initialization
    opendota --help

    # Information about OpenDota methods
    opendota - --help

    # Run methods
    opendota search_team Virtus
    opendota get_match 4080778303