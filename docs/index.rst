Welcome to <OPENDOTA/> API's documentation!
===========================================

A python interface for <OPENDOTA/> API

The :code:`OpenDota` class provided with the package serves as a python
interface for the original OpenDota API in the form of a thin wrapper.
The class assumes some familiarity with the OpenDota API.

All method calls return serializable python objects, as return by the API,
in most cases a dict or a list. Response data is stored as JSON in a local
directory (Default: :code:`~/dota2`), to prevent the load on OpenDota API.

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

About OpenDota API
------------------

The OpenDota API provides Dota 2 related data including advanced match data
extracted from match replays.

OpenDota API Documentation: https://docs.opendota.com/

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
