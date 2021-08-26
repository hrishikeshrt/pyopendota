#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Wrapper for <OPENDOTA/> API

The OpenDota API provides Dota 2 related data including advanced match data
extracted from match replays.

OpenDota API Documentation: https://docs.opendota.com/

About
-----

The OpenDota class serves as a python interface for the original OpenDota API
in the form of a thin wrapper. The class assumes some familiarity with the
OpenDota API.

All method calls return serializable python objects, as return by the API,
in most cases a dict or a list. Response data is stored as JSON in a local
directory (Default: ~/dota2), to prevent the load on OpenDota API.

Features
--------

* Functions for the most frequently used API calls
* Ability to authenticate using API key
* In-built and cusomizable limit to protect against frequent API calls
* Local file-based storage for frequent requests (persistent cache)

@author: Hrishikesh Terdalkar
"""

import os
import time
import json
import logging
from urllib.parse import urlsplit, urlunsplit

import attr
import requests

###############################################################################

logger = logging.getLogger(__name__)

###############################################################################

FREQ_LOW = 10
FREQ_MEDIUM = 20
FREQ_HIGH = 30

###############################################################################


@attr.s
class OpenDota:
    """
    <OPENDOTA/> API Interface

    Creates an instance of connection to OpenDota API.
    All methods return serializable python objects, which are also stored
    as JSON in the `data_dir` for future calls.
    All methods take a boolean argument `force` which, if `True`, will fetch
    the data again even if it is available in the data directory.

    Parameters
    ----------
        data_dir: str, (optional)
            Path to data directory for storing responses to API calls
            The default is ~/dota2.
        api_key: str, (optional)
            If you have an OpenDota API key
            The default is None.
        delay: int, (optional)
            Delay in seconds between two consecutive API calls.
            It is recommended to keep this at least 3 seconds, to
            prevent hitting the daily API limit.
            If you have an API key, this value is ignored.
            The default is 3.
        api_url: str, (optional)
            URL to OpenDota API.
            It is recommended to not change this value.
    """

    data_dir: str = attr.ib(default=None)
    api_url: str = attr.ib(default="https://api.opendota.com/api", repr=False)
    api_key: str = attr.ib(default=None, repr=False)
    delay: int = attr.ib(default=3, repr=False)

    def __attrs_post_init__(self):
        self.session = requests.Session()
        if self.api_key is not None:
            self.session.headers['Authorization'] = f'Bearer {self.api_key}'
        if self.data_dir is None:
            self.data_dir = os.path.join(os.path.expanduser("~"), "dota2")
        os.makedirs(self.data_dir, exist_ok=True)

    # ----------------------------------------------------------------------- #

    def request(self, url, *, post=False, data={}, filename=None, force=False):
        """Make a GET or POST request to <OPENDOTA/> API

        Parameters
        ----------
            url: str
                API path to query
            post: bool, (optional)
                Make a POST request.
                The default is False.
            data: dict, (optional)
                Query Data.
                The default is {}.
            filename: str, (optional)
                Save the data to this file.
                The default is None.
            force: bool, (optional)
                Force-fetch and overwrite data.
                The default is False.

        Returns
        -------
            object:
                Result of the API call deserialized as a python object
        """

        path = None
        if filename is not None:
            path = os.path.join(self.data_dir, filename)
            if not force and os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    logger.info(
                        f"Loading previously fetched data from '{filename}'."
                    )
                    return json_data
                except Exception:
                    pass

        if self.api_key is None:
            time.sleep(self.delay)
        else:
            data["api_key"] = self.api_key

        url_parts = list(urlsplit(self.api_url))
        url_parts[2] += url
        if not post:
            url_parts[3] = "&".join([f"{k}={v}" for k, v in data.items()])

        query_url = urlunsplit(url_parts)
        logger.info("Query URL:", query_url)

        if not post:
            r = self.session.get(query_url)
        else:
            r = self.session.post(query_url, data=data)

        content = r.content.decode("utf-8")
        json_data = json.loads(content)

        if json_data and "error" in json_data:
            logger.warning(f"Could not fetch '{url}' ({json_data['error']}).")
            return None

        if path is not None:
            with open(path, "w") as f:
                json.dump(json_data, f, ensure_ascii=False)
        return json_data

    def get(self, *args, **kwargs):
        """
        Make a GET request to <OPENDOTA/> API.

        Calls .request() with `post=False`
        """
        kwargs['post'] = False
        return self.request(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Make a POST request to <OPENDOTA/> API

        Calls .request() with `post=True`
        """
        kwargs['post'] = True
        return self.request(*args, **kwargs)

    # ----------------------------------------------------------------------- #
    # Request

    def request_parse(self, match_id):
        """Submit a new parse request"""
        logger.info(f"Requesting parse for match {match_id}")
        url = f"/request/{match_id}"
        return self.post(url)

    def request_status(self, job_id):
        """Get parse request state"""
        url = f"/request/{job_id}"
        return self.get(url)

    # ----------------------------------------------------------------------- #
    # Static Game Data (mirrored from the dotaconstants repository)

    def get_constant_names(self, force=False):
        """Get an array of available resources"""
        url = "/constants"
        filename = "constants.json"
        return self.get(url, filename=filename, force=force)

    def get_constants(self, resource=None, force=False):
        """
        Get static game data for specified resource(s)
        (mirrored from the dotaconstants repository)

        Parameters
        ----------
            resource: str or list, indicating name or names of resources
        """
        if resource is not None:
            if isinstance(resource, str):
                resource = [resource]
            if not isinstance(resource, list):
                logger.error(
                    "`resources' must be a string or a list of strings, "
                    f"not `{type(resource)}'"
                )
                return None
        else:
            resource = self.get_constant_names(force=force)

        constants = {}
        for res in resource:
            url = f"/constants/{res}"
            filename = f"constants_{res}.json"
            constants[res] = self.get(url, filename=filename, force=force)
        return constants

    # ----------------------------------------------------------------------- #
    # Hero

    def get_heroes(self, force=False):
        """Get hero data"""
        url = "/heroes"
        filename = "heroes.json"
        return self.get(url, filename=filename, force=force)

    def get_hero_stats(self, force=False):
        """Get stats about hero performance in recent matches"""
        url = "/heroStats"
        filename = "hero_stats.json"
        return self.get(url, filename=filename, force=force)

    def get_hero_benchmarks(self, hero_id, force=False):
        """Get benchmarks for a hero"""
        url = "/benchmarks"
        filename = f"benchmarks_{hero_id}.json"
        data = {"hero_id": hero_id}
        return self.get(url, filename=filename, data=data, force=force)

    # ----------------------------------------------------------------------- #
    # Leagues

    def get_leagues(self, force=False):
        """Get a list of leagues"""
        url = "/leagues"
        filename = "leagues.json"
        return self.get(url, filename=filename, force=force)

    def get_league(self, league_id, force=False):
        """Get data for a league"""
        url = f"/leagues/{league_id}"
        filename = f"league_{league_id}.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # League Specific

    def get_league_matches(self, league_id, force=False):
        """Get matches from a league"""
        url = f"/leagues/{league_id}/matches"
        filename = f"league_{league_id}_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_league_teams(self, league_id, force=False):
        """Get teams from a league"""
        url = f"/leagues/{league_id}/teams"
        filename = f"league_{league_id}_teams.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Teams

    def get_teams(self, force=False):
        """Get team data"""
        url = "/teams"
        filename = "teams.json"
        teams = self.get(url, filename=filename, force=force)
        for team in teams:
            filename = f"team_{team['team_id']}.json"
            path = os.path.join(self.data_dir, filename)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(team, f, ensure_ascii=False)
        return teams

    def get_team(self, team_id, force=False):
        """Get data for a team"""
        url = f"/teams/{team_id}"
        filename = f"team_{team_id}.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Team Specific

    def get_team_matches(self, team_id, force=False):
        """Get matches for a team"""
        url = f"/teams/{team_id}/matches"
        filename = f"team_{team_id}_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_team_players(self, team_id, current=True, force=False):
        """Get players who have played for a team"""
        url = f"/teams/{team_id}/players"
        filename = f"team_{team_id}_players.json"
        players = self.get(url, filename=filename, force=force)
        if current:
            return [
                player
                for player in players
                if player["is_current_team_member"]
            ]
        else:
            return players

    def get_team_heroes(self, team_id, force=False):
        """Get heroes for a team"""
        url = f"/teams/{team_id}/heroes"
        filename = f"team_{team_id}_heroes.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Matches

    def get_match(self, match_id, force=False):
        url = f"/matches/{match_id}"
        filename = f"match_{match_id}.json"
        return self.get(url, filename=filename, force=force)

    def get_pro_matches(self, force=False):
        url = "/proMatches"
        filename = "pro_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_live(self):
        """Get top currently ongoing live games"""
        url = "/live"
        return self.get(url)

    # ----------------------------------------------------------------------- #
    # Players

    def get_player(self, account_id, force=False):
        """Player data"""
        url = f"/players/{account_id}"
        filename = f"player_{account_id}.json"
        return self.get(url, filename=filename, force=force)

    def get_pro_players(self, force=False):
        url = "/proPlayers"
        filename = "pro_players.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Player Specific

    def get_player_heroes(self, player_id, force=False):
        url = f"/players/{player_id}/heroes"
        filename = f"player_{player_id}_heroes.json"
        # TODO: Include query parameters
        data = {}
        return self.get(url, filename=filename, data=data, force=force)

    def get_player_matches(
        self, player_id, request_parse=False, days=180, force=False
    ):
        """Matches played by a player"""
        url = f"/players/{player_id}/matches"
        filename = f"player_{player_id}_matches.json"
        data = {"date": days}
        matches = self.get(url, filename=filename, data=data, force=force)
        if request_parse:
            for match in matches:
                match_id = match["match_id"]
                if match["version"] is None or match["version"] < 20:
                    json_data = self.request_parse(match_id)
                    logger.info("Match ID:", match_id)
                    logger.info("Job ID:", json_data["job"]["jobId"])
        return matches

    def get_player_ratings(self, player_id, force=False):
        """Player rating history"""
        url = f"/players/{player_id}/ratings"
        filename = f"player_{player_id}_ratings.json"
        return self.get(url, filename=filename, force=force)

    def get_player_rankings(self, player_id, force=False):
        """Player hero rankings"""
        url = f"/players/{player_id}/rankings"
        filename = f"player_{player_id}_rankings.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Search

    def search_hero(self, search_key=None, attack_type=None, roles=None):
        """Search for a hero by name, attack type or roles"""
        results = []
        for hero in self.get_heroes():
            conditions = []
            if search_key is not None:
                conditions.append(
                    search_key.lower() in hero["localized_name"].lower()
                )
            if attack_type is not None:
                conditions.append(attack_type.title() == hero["attack_type"])
            if roles is not None:
                if isinstance(roles, str):
                    roles = [roles]
                conditions.append(
                    all([role.title() in hero["roles"] for role in roles])
                )
            if all(conditions):
                results.append(hero)
        return results

    def search_league(self, search_key):
        """Search for a league"""
        return [
            league
            for league in self.get_leagues()
            if search_key.lower() in league["name"].lower()
        ]

    def search_team(self, search_key):
        """Search for a team by name or tag"""
        return [
            team
            for team in self.get_teams()
            if search_key.lower() in team["name"].lower()
            or search_key.lower() == team["tag"].lower()
        ]

    def search_player(self, search_key):
        """Search for a player"""
        url = "/search"
        data = {"q": search_key}
        return self.get(url, data=data)

    # ----------------------------------------------------------------------- #
    # Database

    def get_schema(self, table_name=None, force=False):
        """Get database schema

        Parameters
        ----------
            table_name: str
                Get schema for table_name
                If None, list the available table names
        """
        url = "/schema"
        filename = "schema.json"
        schema = self.get(url, filename=filename, force=force)

        if table_name is None:
            return sorted(set([field["table_name"] for field in schema]))
        else:
            return {
                field["column_name"]: field["data_type"]
                for field in schema
                if table_name == field["table_name"]
            }

    def explorer(self, sql, debug=False):
        """Submit arbitrary PostgreSQL queries to the database"""
        url = "/explorer"
        data = {"sql": sql}
        result = self.get(url, data=data)
        if debug:
            return result
        return result.get("rows", [])

    def query(self, *args, **kwargs):
        """Submit arbitrary PostgreSQL queries to the database"""
        return self.explorer(*args, **kwargs)

    # ----------------------------------------------------------------------- #

    def update_data(self, frequency=FREQ_HIGH):
        """Update core data

        It is recommended to use utility constants, FREQ_LOW, FREQ_MEDIUM or
        FREQ_HIGH to specifcy frequency.

        Parameters
        ----------
            frequency: int
                FREQ_HIGH: update data that only changes frequently
                   (e.g. teams)
                FREQ_MEDIUM: update data that changes with a moderate frequency
                   (e.g. hero benchmarks)
                FREQ_LOW: update data that changes very infrequently
                   (e.g. heroes)
        """
        if frequency <= FREQ_HIGH:
            self.get_teams(force=True)

        if frequency <= FREQ_MEDIUM:
            heroes = self.get_heroes()
            for hero in heroes:
                self.get_hero_benchmarks(hero["id"], force=True)

        if frequency <= FREQ_LOW:
            self.get_constants(force=True)
            self.get_heroes(force=True)

    # ----------------------------------------------------------------------- #


###############################################################################
