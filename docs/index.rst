Welcome to <OPENDOTA/> API's documentation!
===========================================

.. image:: https://img.shields.io/pypi/v/pyopendota?color=success
        :target: https://pypi.python.org/pypi/pyopendota

.. image:: https://readthedocs.org/projects/pyopendota/badge/?version=latest
        :target: https://pyopendota.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/pyopendota
        :target: https://pypi.python.org/pypi/pyopendota
        :alt: Python Version Support

.. image:: https://img.shields.io/github/issues/hrishikeshrt/pyopendota
        :target: https://github.com/hrishikeshrt/pyopendota/issues
        :alt: GitHub Issues

.. image:: https://img.shields.io/github/followers/hrishikeshrt?style=social
        :target: https://github.com/hrishikeshrt
        :alt: GitHub Followers

.. image:: https://img.shields.io/twitter/follow/hrishikeshrt?style=social
        :target: https://twitter.com/hrishikeshrt
        :alt: Twitter Followers

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
========

* Transparent wrapper for majority of the API calls
* Ability to authenticate using API key
* In-built and cusomizable limit to protect against frequent API calls
* Local file-based storage for frequent requests
* Basic CLI using :code:`fire`

About OpenDota API
==================

The OpenDota API provides Dota 2 related data including advanced match data
extracted from match replays.

OpenDota API Documentation: https://docs.opendota.com/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   modules
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
