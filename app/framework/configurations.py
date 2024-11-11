#!python3
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 5.
# Modified: 2024. 10.
#

"""
configurations

- 기본 설정 구조 정의
- 구조 활용 함수 정의
"""

from pydantic import BaseModel

from roots import Path, ROOT, ROOT_APPDATA


#
# configurations
#
class AppPaths(BaseModel):
    log: str

class AppAttributes(BaseModel):
    appname: str

class Configurations(BaseModel):
    path: AppPaths
    attributes: AppAttributes


#
# functions
#
def set_defaults() -> Configurations:
    return Configurations(path=
        AppPaths(
            log=str(ROOT_APPDATA("log"))
        ),
        attributes=AppAttributes(
            appname=str(ROOT(".").name)
        )
    )

def load(filepath:Path=None) -> Configurations:
    if filepath is None :
        filepath = ROOT_APPDATA("configs.json")

    try:
        with open(filepath, "r", encoding="utf-8") as fp:
            configs = Configurations.model_validate_json(fp.read())

    except Exception as e:
        print(f"Invalid a configuration file ({filepath}), recreating a config file to the defaults.")
        if filepath.exists():
            backupfile = filepath.with_name(f"{filepath.stem}_bak{filepath.suffix}")
            print(f"Backup old file to {backupfile}")
            filepath.rename(backupfile)

        configs = set_defaults()
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(configs.model_dump_json(indent=4))
    
    return configs


#
# unittest
#
def unittest():
    configs = set_defaults()
    print(configs)
    load()

if __name__ == "__main__":
    from __init__ import print

    unittest()
    print("done.")
