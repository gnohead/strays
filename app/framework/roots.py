#!python3
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 10.
# 

import os, sys
from pathlib import Path

ROOT = lambda pt: Path(os.path.commonpath([__file__, sys.executable])).joinpath(pt).resolve()
ROOT_FRAMEWORK = lambda pt: ROOT(__file__).parent.joinpath(pt).resolve()
ROOT_APPDATA = lambda pt: ROOT("./__appdata__").joinpath(pt).resolve()
ROOT_APPDATA(".").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    from __init__ import print

    print("done.")