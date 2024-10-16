#!python3
#-*- coding: utf-8 -*-

import os, sys
import json

from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel, ValidationError

ROOT = lambda pt: Path(os.path.commonpath([__file__, sys.executable])).joinpath(pt).resolve()
ROOT_FRAMEWORK = lambda pt: ROOT(__file__).parent.joinpath(pt).resolve()
ROOT_APPDATA = lambda pt: ROOT("./__appdata__").joinpath(pt).resolve()
ROOT_APPDATA(".").mkdir(parents=True, exist_ok=True)

class AppPaths(BaseModel):
    log: str = str(ROOT_APPDATA("log"))

class AppAttributes(BaseModel):
    name: str = str(ROOT(".").name)

class Configurations(BaseModel):
    path: AppPaths = AppPaths()
    attributes: AppAttributes = AppAttributes()

def load_configurations(filepath:Path=None) -> Configurations:
    if filepath is None :
        filepath = ROOT_APPDATA("configs.json")

    print(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as fp:
            configs = Configurations(**json.load(fp))

    except:
        configs = Configurations()
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(configs.model_dump_json(indent=4))
    
    return configs
