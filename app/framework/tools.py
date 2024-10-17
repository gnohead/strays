#!python
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 5.
# Modified: 2024. 10.
#

"""
tools

- 프로그램 제작에 필요한 도구들을 모아놓은 모듈
"""

import os
import uuid
import hashlib
import random
import shutil
import zipfile
import pickle
import subprocess

from pathlib import Path
from dotenv import dotenv_values
from datetime import datetime, timedelta
from pytz import timezone
from typing import List, Any, Tuple


def add_environments(envfile:str):
    envvars = dotenv_values(envfile)
    for k, v in envvars.items():
        if k in os.environ.keys():
            continue
        else:
            os.environ[k] = v
            print(f"env init> {k}={v}")


def get_git_branch() -> str:
    # git 명령어를 실행하여 현재 브랜치의 이름을 가져옵니다.
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    # 결과에서 브랜치 이름을 추출합니다.
    current_branch = result.stdout.strip()
    return current_branch


def is_dev() -> bool:
    return "dev" == get_git_branch()


def gen_uuid():
    return uuid.uuid4()


def hash_uuid():
    # UUID 생성
    uuid_obj = uuid.uuid4()
    # UUID를 문자열로 변환
    uuid_str = str(uuid_obj)
    # SHA-256 해시 생성
    sha256_hash = hashlib.sha256(uuid_str.encode())
    # 해시를 16진수 문자열로 변환
    hash_str = sha256_hash.hexdigest()
    return hash_str


def gen_key(len=64):
    m1 = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E', '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J' }
    m2 = { '0': 'K', '1': 'L', '2': 'M', '3': 'N', '4': 'O', '5': 'P', '6': 'Q', '7': 'R', '8': 'S', '9': 'T' }
    m3 = { '0': 'U', '1': 'V', '2': 'W', '3': 'X', '4': 'Y', '5': 'Z', '6': '2', '7': '3', '8': '5', '9': '7' }
    m4 = { 'A': '1', 'B': '4', 'C': '6', 'D': '8', 'E': '9', 'F': '0', 'G': '2', 'H': '3', 'I': '5', 'J': '7' }
    m5 = { 'a': '1', 'b': '4', 'c': '6', 'd': '8', 'e': '9', 'f': '0', 'g': '2', 'h': '3', 'i': '5', 'j': '7' }
    m6 = { 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J' }
    m7 = { 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T' }

    hash_string = hash_uuid()
    output_str = ''.join(random.choice([m1, m2, m3, m4, m5, m6, m7]).get(char, char) for char in hash_string)

    return ''.join(random.choice(output_str) for _ in range(len))


def gen_timestamp() -> str:
    tz = timezone('Asia/Seoul')
    return datetime.now(tz).strftime("%Y%m%d%H%M%S%f")


def remove_oldest_files(dirpath:str, prefix:str, type:str, remaining_count:int):
    fpath = lambda x: Path(dirpath).joinpath(x).resolve().absolute().as_posix()

    similarfiles = [fpath(x) for x in os.listdir(dirpath) if x.startswith(prefix) and x.endswith(type)]
    similarfiles.sort(key=os.path.getctime)
    while len(similarfiles) >= remaining_count:
        oldest_file = similarfiles.pop(0)
        print(f"pop: {oldest_file}")
        os.remove(oldest_file)


def extract_zip(zippath:str, targetpath:str, purge_when_exists:bool=True):
    """
    주어진 zip 파일을 특정 경로에 해제하는 함수입니다.

    Parameters:
        zippath (str): 해제할 zip 파일의 경로
        targetpath (str): 해제된 파일들을 저장할 경로
        purge_when_exists (bool, optional): targetpath가 이미 존재할 경우 삭제 여부. 기본값은 True입니다.

    Returns:
        None
    """
    if purge_when_exists and Path(targetpath).exists():
        # 이미 폴더가 있으면 제거
        print(f"removing : {targetpath}")
        shutil.rmtree(targetpath)

    # zippath 파일을 targetpath 디렉토리에 해제
    with zipfile.ZipFile(zippath, 'r') as zip_ref:
        zip_ref.extractall(targetpath)

        print(f"extracted : {zippath} to {targetpath}")


def join_path(directory:str, filename:str) -> str:
    return Path(directory).joinpath(filename).resolve().absolute().as_posix()


def list_files(directory:str, extension:str) -> List[str]:
    files = list(Path(directory).rglob(f"*.{extension}"))
    return [file.as_posix() for file in files]


def export_to_pickle(filepath:str, data:Any) -> None:
    with open(filepath, "wb") as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)


def import_from_pickle(filepath:str) -> Any:
    with open(filepath, "rb") as fp:
        return pickle.load(fp)


def get_date_interval(after_days:int, date_format:str="%Y-%m-%d") -> Tuple[str, str]:
    today = datetime.today()

    end = today.strftime(date_format)
    begin = (today - timedelta(days=after_days)).strftime(date_format)
    
    return (begin, end)


def shift_alphabet(text):
    result = []
    
    for char in text:
        # 소문자일 경우
        if 'a' <= char <= 'z':
            # z일 경우 a로
            new_char = chr((ord(char) - ord('a') + 1) % 26 + ord('a'))
        # 대문자일 경우
        elif 'A' <= char <= 'Z':
            # Z일 경우 A로
            new_char = chr((ord(char) - ord('A') + 1) % 26 + ord('A'))
        # 숫자일 경우
        elif '0' <= char <= '9':
            new_char = chr((ord(char) - ord('0') + 1) % 10 + ord('0'))        
        else:
            # 알파벳이 아닌 경우 그대로 유지
            new_char = char
        
        result.append(new_char)
    
    return ''.join(result)


def restore_alphabet(text):
    result = []
    
    for char in text:
        # 소문자일 경우
        if 'a' <= char <= 'z':
            # a일 경우 z로
            new_char = chr((ord(char) - ord('a') - 1) % 26 + ord('a'))
        # 대문자일 경우
        elif 'A' <= char <= 'Z':
            # A일 경우 Z로
            new_char = chr((ord(char) - ord('A') - 1) % 26 + ord('A'))
        # 숫자일 경우
        elif '0' <= char <= '9':
            new_char = chr((ord(char) - ord('0') - 1) % 10 + ord('0'))        
        else:
            # 알파벳이 아닌 경우 그대로 유지
            new_char = char
        
        result.append(new_char)
    
    return ''.join(result)


#
# unittest
#
def unittest():
    uuid = gen_uuid()
    print(uuid)

    unique_key = gen_key()
    print(unique_key)

    ts = gen_timestamp()
    print(ts)
    
def unittest2():
    branch_name = get_git_branch()
    print(branch_name)

if __name__ == "__main__":
    from __init__ import print

    unittest()
    unittest2()
    print("done.")
