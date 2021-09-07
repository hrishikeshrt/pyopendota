#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console Script for <OPENDOTA/> API

@author: Hrishikesh Terdalkar
"""

import fire
from .opendota import OpenDota

###############################################################################


def main():
    """
    Console Script for <OPENDOTA/> API
    Powered by `python-fire`
    """
    fire.Fire(OpenDota)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())  # pragma: no cover
