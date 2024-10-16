#!python3
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 10.
# 

import os, sys
import json

from pathlib import Path
from pydantic import BaseModel, Field

ROOT = lambda pt: Path(os.path.commonpath([__file__, sys.executable])).joinpath(pt).resolve()
ROOT_FRAMEWORK = lambda pt: ROOT(__file__).parent.joinpath(pt).resolve()
ROOT_APPDATA = lambda pt: ROOT("./__appdata__").joinpath(pt).resolve()
ROOT_APPDATA(".").mkdir(parents=True, exist_ok=True)


class AppPaths(BaseModel):
    log: str = Field(default=str(ROOT_APPDATA("log")))

class AppAttributes(BaseModel):
    appname: str = str(ROOT(".").name)

class Configurations(BaseModel):
    path: AppPaths = AppPaths()
    attributes: AppAttributes = AppAttributes()

def load_configurations(filepath:Path=None) -> Configurations:
    if filepath is None :
        filepath = ROOT_APPDATA("configs.json")

    try:
        with open(filepath, "r", encoding="utf-8") as fp:
            configs = Configurations.model_validate_json(fp.read())
            print(configs)

    except Exception as e:
        print(repr(e))

        configs = Configurations()
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(configs.model_dump_json(indent=4))
    
    return configs


if __name__ == "__main__":
    from __init__ import print

    print("done.")