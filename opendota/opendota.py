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
"""

import os
import time
import json
import logging
from typing import Any, List
from urllib.parse import urlsplit, urlunsplit
from dataclasses import dataclass, field

import requests

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################

OPENDOTA_API_URL = "https://api.opendota.com/api"

###############################################################################

FREQ_LOW = 10
FREQ_MEDIUM = 20
FREQ_HIGH = 30

###############################################################################
# Default Fantasy Multipliers

FANTASY = {
    'kills': 0.3,
    'deaths': -0.3,
    'assists': 0,
    'last_hits': 0.003,
    'gold_per_min': 0.002,
    'xp_per_min': 0,
    'tower_kills': 1,
    'tower_damage': 0,
    'hero_damage': 0,
    'courier_kills': 0,
    'observer_kills': 0,
    'sentry_kills': 0,
    'roshan_kills': 1,
    'teamfight': 3,
    'observer_placed': 0.5,
    'sentry_placed': 0,
    'camps_stacked': 0.5,
    'runes_grabbed': 0.25,
    'first_blood': 4,
    'stuns': 0.05,
    'hero_healing': 0,

    # Add '_base' suffix to the parameter for specifying base score
    'deaths_base': 3,
}

# TODO: potential metrics
# - kill_streaks
# - multi_kills

FANTASY_RECOMMENDED = {
    'kills': 0.15,
    'assists': 0.05,
    'tower_kills': 0.5,
    'tower_damage': 0.0002,
    'hero_damage': 0.0001,
    'courier_kills': 0.2,
    'observer_kills': 0.5,
    'roshan_kills': 1.5,
    'first_blood': 2
}

###############################################################################


@dataclass
class OpenDota:
    """
    <OPENDOTA/> API Interface

    Instance of a connection to OpenDota API.
    All methods return serializable python objects, which are also stored
    as JSON in the :code:`data_dir` for future calls.
    All methods take a boolean argument :code:`force` which, if True,
    will fetch the data again even if it is available in the data directory.

    Parameters
    ----------
        data_dir: str, (optional)
            Path to data directory for storing responses to API calls
            The default is :code:`~/dota2`.
        api_key: str, (optional)
            If you have an OpenDota API key
            The default is None.
        delay: int, (optional)
            Delay in seconds between two consecutive API calls.
            It is recommended to keep this at least 3 seconds, to
            prevent hitting the daily API limit.
            If you have an API key, this value is ignored.
            The default is 3.
        fantasy: dict, (optional)
            Fantasy DotA2 Configuration
            Utility constant FANTASY holds the standard values
            and is used as default.
            Keys of the :code:`fantasy` will override the default values.
            They must be a subset of the keys of :code:`FANTASY`.

            Parameters ending with :code:`_base` are used as base values,
            while others are used as multipliers.
            e.g.
            :code:`deaths = -0.3` and :code:`deaths_base = 3` results in the
            calculation as, :code:`death_score = 3 + (number_of_deaths * -0.3)`
            If :code:`_base` parameter is absent, it's assumed to be 0.
        api_url: str, (optional)
            URL to OpenDota API.
            It is recommended to not change this value.
    """

    data_dir: str = field(default=None)
    api_key: str = field(default=None, repr=False)
    delay: int = field(default=3, repr=False)
    fantasy: dict = field(default=None, repr=False)
    api_url: str = field(default=OPENDOTA_API_URL, repr=False)

    def __post_init__(self):
        self._session = requests.Session()
        if self.api_key is not None:
            self._session.headers['Authorization'] = f'Bearer {self.api_key}'

        if self.data_dir is None:
            self.data_dir = os.path.join(os.path.expanduser("~"), "dota2")
        os.makedirs(self.data_dir, exist_ok=True)

        default_fantasy = FANTASY.copy()
        if self.fantasy is not None:
            default_fantasy.update(self.fantasy)
        self.fantasy = default_fantasy

    # ----------------------------------------------------------------------- #

    def request(
        self,
        url: str,
        *,
        post: bool = False,
        data: dict = None,
        filename: str = None,
        force: bool = False
    ) -> Any:
        """
        Make a GET or POST request to <OPENDOTA/> API

        Parameters
        ----------
            url: str
                API path to query
            post: bool, (optional)
                Make a POST request.
                The default is False.
            data: dict, (optional)
                Query Data.
                The default is None.
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
                    LOGGER.info(
                        f"Loading previously fetched data from '{filename}'."
                    )
                    return json_data
                except Exception:
                    pass

        data = data or {}
        if self.api_key is None:
            time.sleep(self.delay)
        else:
            data["api_key"] = self.api_key

        url_parts = list(urlsplit(self.api_url))
        url_parts[2] += url
        if not post:
            url_parts[3] = "&".join([f"{k}={v}" for k, v in data.items()])

        query_url = urlunsplit(url_parts)
        LOGGER.info("Query URL:", query_url)

        if not post:
            r = self._session.get(query_url)
        else:
            r = self._session.post(query_url, data=data)

        content = r.content.decode("utf-8")
        json_data = json.loads(content)

        if json_data and "error" in json_data:
            LOGGER.warning(f"Could not fetch '{url}' ({json_data['error']}).")
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

    def request_parse(self, match_id: int or str):
        """Submit a new parse request"""
        LOGGER.info(f"Requesting parse for match {match_id}")
        url = f"/request/{match_id}"
        return self.post(url)

    def request_status(self, job_id: int or str):
        """Get parse request state"""
        url = f"/request/{job_id}"
        return self.get(url)

    # ----------------------------------------------------------------------- #
    # Static Game Data (mirrored from the dotaconstants repository)

    def get_constant_names(self, force: bool = False):
        """Get an array of available resources"""
        url = "/constants"
        filename = "constants.json"
        return self.get(url, filename=filename, force=force)

    def get_constants(self, resource: str = None, force: bool = False):
        """
        Get static game data for specified resource(s)
        (mirrored from the dotaconstants repository)

        Parameters
        ----------
            resource: str or list,
                Name or names of resources
        """
        if resource is not None:
            if isinstance(resource, str):
                resource = [resource]
            if not isinstance(resource, list):
                LOGGER.error(
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

    def get_heroes(self, force: bool = False):
        """Get hero data"""
        url = "/heroes"
        filename = "heroes.json"
        return self.get(url, filename=filename, force=force)

    def get_hero_stats(self, force: bool = False):
        """Get stats about hero performance in recent matches"""
        url = "/heroStats"
        filename = "hero_stats.json"
        return self.get(url, filename=filename, force=force)

    def get_hero_benchmarks(self, hero_id: int or str, force: bool = False):
        """Get benchmarks for a hero"""
        url = "/benchmarks"
        filename = f"benchmarks_{hero_id}.json"
        data = {"hero_id": hero_id}
        return self.get(url, filename=filename, data=data, force=force)

    # ----------------------------------------------------------------------- #
    # Leagues

    def get_leagues(self, force: bool = False):
        """Get a list of leagues"""
        url = "/leagues"
        filename = "leagues.json"
        return self.get(url, filename=filename, force=force)

    def get_league(self, league_id: int or str, force: bool = False):
        """Get data for a league"""
        url = f"/leagues/{league_id}"
        filename = f"league_{league_id}.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # League Specific

    def get_league_matches(self, league_id: int or str, force: bool = False):
        """Get matches from a league"""
        url = f"/leagues/{league_id}/matches"
        filename = f"league_{league_id}_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_league_teams(self, league_id: int or str, force: bool = False):
        """Get teams from a league"""
        url = f"/leagues/{league_id}/teams"
        filename = f"league_{league_id}_teams.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Teams

    def get_teams(self, force: bool = False):
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

    def get_team(self, team_id: int or str, force: bool = False):
        """Get data for a team"""
        url = f"/teams/{team_id}"
        filename = f"team_{team_id}.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Team Specific

    def get_team_matches(self, team_id: int or str, force: bool = False):
        """Get matches for a team"""
        url = f"/teams/{team_id}/matches"
        filename = f"team_{team_id}_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_team_players(
        self,
        team_id: int or str,
        current: bool = True,
        force: bool = False
    ):
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

    def get_team_heroes(self, team_id: int or str, force: bool = False):
        """Get heroes for a team"""
        url = f"/teams/{team_id}/heroes"
        filename = f"team_{team_id}_heroes.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Matches

    def get_match(self, match_id: int or str, force: bool = False):
        """Get match data"""
        url = f"/matches/{match_id}"
        filename = f"match_{match_id}.json"
        return self.get(url, filename=filename, force=force)

    def get_pro_matches(self, force: bool = False):
        """Get a list of pro matches"""
        url = "/proMatches"
        filename = "pro_matches.json"
        return self.get(url, filename=filename, force=force)

    def get_live(self):
        """Get top currently ongoing live games"""
        url = "/live"
        return self.get(url)

    # ----------------------------------------------------------------------- #
    # Players

    def get_player(self, account_id: int or str, force: bool = False):
        """Player data"""
        url = f"/players/{account_id}"
        filename = f"player_{account_id}.json"
        return self.get(url, filename=filename, force=force)

    def get_pro_players(self, force: bool = False):
        """Get a list of pro players"""
        url = "/proPlayers"
        filename = "pro_players.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Player Specific

    def get_player_heroes(self, player_id: int or str, force: bool = False):
        """Get heroes played by a player"""
        url = f"/players/{player_id}/heroes"
        filename = f"player_{player_id}_heroes.json"
        # TODO: Include query parameters
        # Parameters described in documentation "/players/{account_id}/heroes"
        # NOTE:
        # - Difficulty: Parameters would somehow need to be in filename,
        #               else the cache loses meaning
        # - Potential Solution: Cache only when no-parameters
        data = {}
        return self.get(url, filename=filename, data=data, force=force)

    def get_player_matches(
        self,
        player_id: int or str,
        request_parse: bool = False,
        days: int = 180,
        force: bool = False
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
                    LOGGER.info("Match ID:", match_id)
                    LOGGER.info("Job ID:", json_data["job"]["jobId"])
        return matches

    def get_player_ratings(self, player_id: int or str, force: bool = False):
        """Player rating history"""
        url = f"/players/{player_id}/ratings"
        filename = f"player_{player_id}_ratings.json"
        return self.get(url, filename=filename, force=force)

    def get_player_rankings(self, player_id: int or str, force: bool = False):
        """Player hero rankings"""
        url = f"/players/{player_id}/rankings"
        filename = f"player_{player_id}_rankings.json"
        return self.get(url, filename=filename, force=force)

    # ----------------------------------------------------------------------- #
    # Search

    def search_hero(
        self,
        search_key: str = None,
        attack_type: str = None,
        roles: List[str] = None
    ):
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

    def search_league(self, search_key: str):
        """Search for a league"""
        return [
            league
            for league in self.get_leagues()
            if search_key.lower() in league["name"].lower()
        ]

    def search_team(self, search_key: str):
        """Search for a team by name or tag"""
        return [
            team
            for team in self.get_teams()
            if search_key.lower() in team["name"].lower()
            or search_key.lower() == team["tag"].lower()
        ]

    def search_player(self, search_key: str):
        """Search for a player"""
        url = "/search"
        data = {"q": search_key}
        return self.get(url, data=data)

    # ----------------------------------------------------------------------- #
    # Fantasy

    def get_fantasy_points(self, match_id: int or str, force: bool = False):
        """
        Get Fantasy Points of All Players from a Match

        Parameters
        ----------

        match_id: int or str
            Match ID

        Returns
        -------
            list:
                List of fantasy profiles of players from the specified match
        """
        match = self.get_match(match_id, force=force)
        fantasy_points = []

        for player in match['players']:
            player_slot = player['player_slot']
            player_side = 'radiant' if player['player_slot'] < 5 else 'dire'
            player_team = match[f'{player_side}_team']
            player_result = (
                'win'
                if match['radiant_win'] == (player_side == 'radiant')
                else 'loss'
            )

            player_fantasy = {
                'player': {
                    'slot': player_slot,
                    'side': player_side,
                    'account_id': player['account_id'],
                    'team_id': player_team['team_id'],
                    'name': player['name'],
                    'team': player_team['name'],
                    'result': player_result
                },
                'fantasy': {
                    'kills': {
                        'value': player['kills']
                    },
                    'deaths': {
                        'value': player['deaths']
                    },
                    'assists': {
                        'value': player['assists']
                    },
                    'last_hits': {
                        'value': player['last_hits'] + player['denies'],
                    },
                    'gold_per_min': {
                        'value': player['gold_per_min']
                    },
                    'xp_per_min': {
                        'value': player['xp_per_min']
                    },
                    'tower_kills': {
                        'value': player['tower_kills']
                    },
                    'tower_damage': {
                        'value': player['tower_damage']
                    },
                    'hero_damage': {
                        'value': player['hero_damage']
                    },
                    'courier_kills': {
                        'value': player['courier_kills']
                    },
                    'observer_kills': {
                        'value': player['observer_kills']
                    },
                    'sentry_kills': {
                        'value': player['sentry_kills']
                    },
                    'roshan_kills': {
                        'value': player['roshan_kills']
                    },
                    'teamfight': {
                        'value': player['teamfight_participation']
                    },
                    'observer_placed': {
                        'value': player['obs_placed']
                    },
                    'sentry_placed': {
                        'value': player['sen_placed']
                    },
                    'camps_stacked': {
                        'value': player['camps_stacked']
                    },
                    'runes_grabbed': {
                        'value': player['rune_pickups']
                    },
                    'first_blood': {
                        'value': int(player['firstblood_claimed'])
                    },
                    'stuns': {
                        'value': player['stuns']
                    },
                    'hero_healing': {
                        'value': player['hero_healing']
                    }
                },
            }

            for param, obj in player_fantasy['fantasy'].items():
                obj['score'] = (
                    self.fantasy.get(f'{param}_base', 0) +
                    self.fantasy[param] * obj['value']
                )
            player_fantasy['total_score'] = sum([
                obj['score']
                for obj in player_fantasy['fantasy'].values()
            ])
            fantasy_points.append(player_fantasy)

        return fantasy_points

    # ----------------------------------------------------------------------- #
    # Database

    def get_schema(self, table_name: str = None, force: bool = False):
        """
        Get database schema

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

    def explorer(self, sql: str, debug: bool = False):
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

    def update_data(self, frequency: int = FREQ_HIGH):
        """
        Update core data

        Parameters
        ----------
            frequency: int
                It is recommended to use utility constants,
                FREQ_LOW, FREQ_MEDIUM or FREQ_HIGH to specifcy frequency.

                FREQ_HIGH: update data that changes frequently
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
