=====
Usage
=====

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
