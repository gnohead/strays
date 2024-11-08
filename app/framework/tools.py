#!python
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 5.
# Modified: 2024. 11.
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
import json
import time

from pathlib import Path
from dotenv import dotenv_values
from datetime import datetime, timedelta
from pytz import timezone, BaseTzInfo
from typing import List, Any, Tuple, Dict, Generator

from pydantic import create_model, BaseModel
 
def create_model_from_data(name: str, data: Dict[str, Any]) -> BaseModel:
    """
    주어진 데이터로부터 Pydantic 모델을 생성합니다.

    Parameters:
        name (str): 모델의 이름
        data (Dict[str, Any]): 모델에 포함될 데이터

    Returns:
        BaseModel: 생성된 Pydantic 모델 인스턴스
    """
    NewModel = create_model(name, **{key: (type(value), ...) for key, value in data.items()})
    return NewModel(**data)


def load_json(filepath: Path) -> BaseModel:
    """
    JSON 파일을 로드하여 Pydantic 모델로 변환합니다.

    Parameters:
        filepath (Path): JSON 파일의 경로

    Returns:
        BaseModel: 생성된 Pydantic 모델 인스턴스
    """
    with open(filepath, "r", encoding="utf-8") as fp:
        return create_model_from_data(filepath.stem, json.load(fp))


def add_environments(envfile: str):
    """
    .env 파일의 환경 변수를 시스템 환경 변수로 추가합니다.

    Parameters:
        envfile (str): .env 파일의 경로
    """
    envvars = dotenv_values(envfile)
    for k, v in envvars.items():
        if k in os.environ.keys():
            continue
        else:
            os.environ[k] = v
            print(f"env init> {k}={v}")


def get_git_branch() -> str:
    """
    현재 Git 브랜치의 이름을 반환합니다.

    Returns:
        str: 현재 Git 브랜치의 이름
    """
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    return result.stdout.strip()


def is_dev() -> bool:
    """
    현재 브랜치가 'dev'인지 확인합니다.

    Returns:
        bool: 현재 브랜치가 'dev'이면 True, 아니면 False
    """
    return "dev" == get_git_branch()


def gen_uuid() -> uuid.UUID:
    """
    UUID를 생성합니다.

    Returns:
        uuid.UUID: 생성된 UUID
    """
    return uuid.uuid4()


def hash_uuid() -> str:
    """
    UUID를 생성하고 SHA-256 해시를 반환합니다.

    Returns:
        str: SHA-256 해시 문자열
    """
    # UUID 생성
    uuid_obj = uuid.uuid4()
    # UUID를 문자열로 변환
    uuid_str = str(uuid_obj)
    # SHA-256 해시 생성
    sha256_hash = hashlib.sha256(uuid_str.encode())
    # 해시를 16진수 문자열로 변환
    hash_str = sha256_hash.hexdigest()
    return hash_str


def gen_key(length: int = 64) -> str:
    """
    지정된 길이의 고유 키를 생성합니다.

    Parameters:
        length (int, optional): 생성할 키의 길이. 기본값은 64입니다.

    Returns:
        str: 생성된 고유 키
    """
    m1 = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E', '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J' }
    m2 = { '0': 'K', '1': 'L', '2': 'M', '3': 'N', '4': 'O', '5': 'P', '6': 'Q', '7': 'R', '8': 'S', '9': 'T' }
    m3 = { '0': 'U', '1': 'V', '2': 'W', '3': 'X', '4': 'Y', '5': 'Z', '6': '2', '7': '3', '8': '5', '9': '7' }
    m4 = { 'A': '1', 'B': '4', 'C': '6', 'D': '8', 'E': '9', 'F': '0', 'G': '2', 'H': '3', 'I': '5', 'J': '7' }
    m5 = { 'a': '1', 'b': '4', 'c': '6', 'd': '8', 'e': '9', 'f': '0', 'g': '2', 'h': '3', 'i': '5', 'j': '7' }
    m6 = { 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J' }
    m7 = { 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T' }

    hash_string = hash_uuid()
    output_str = ''.join(random.choice([m1, m2, m3, m4, m5, m6, m7]).get(char, char) for char in hash_string)

    return ''.join(random.choice(output_str) for _ in range(length))


def remove_oldest_files(dirpath: str, prefix: str, type: str, remaining_count: int):
    """
    지정된 디렉토리에서 가장 오래된 파일들을 삭제하여 남은 파일의 수를 유지합니다.

    Parameters:
        dirpath (str): 파일들이 위치한 디렉토리 경로
        prefix (str): 파일 이름의 접두사
        type (str): 파일 확장자
        remaining_count (int): 남길 파일의 수
    """
    fpath = lambda x: Path(dirpath).joinpath(x).resolve().absolute().as_posix()

    similarfiles = [fpath(x) for x in os.listdir(dirpath) if x.startswith(prefix) and x.endswith(type)]
    similarfiles.sort(key=os.path.getctime)
    while len(similarfiles) >= remaining_count:
        oldest_file = similarfiles.pop(0)
        print(f"pop: {oldest_file}")
        os.remove(oldest_file)


def extract_zip(zippath: str, targetpath: str, purge_when_exists: bool=True):
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


def join_path(directory: str, filename: str) -> str:
    """
    디렉토리와 파일 이름을 결합하여 절대 경로를 반환합니다.

    Parameters:
        directory (str): 디렉토리 경로
        filename (str): 파일 이름

    Returns:
        str: 결합된 절대 경로
    """
    return Path(directory).joinpath(filename).resolve().absolute().as_posix()


def list_files(directory: str, extension: str) -> List[str]:
    """
    지정된 디렉토리에서 주어진 확장자를 가진 파일들의 목록을 반환합니다.

    Parameters:
        directory (str): 디렉토리 경로
        extension (str): 파일 확장자

    Returns:
        List[str]: 파일 경로 목록
    """
    files = list(Path(directory).rglob(f"*.{extension}"))
    return [file.as_posix() for file in files]


def export_to_pickle(filepath: str, data: Any) -> None:
    """
    데이터를 pickle 파일로 내보냅니다.

    Parameters:
        filepath (str): 저장할 pickle 파일의 경로
        data (Any): 저장할 데이터
    """
    with open(filepath, "wb") as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)


def import_from_pickle(filepath: str) -> Any:
    """
    pickle 파일에서 데이터를 불러옵니다.

    Parameters:
        filepath (str): 불러올 pickle 파일의 경로

    Returns:
        Any: 불러온 데이터
    """
    with open(filepath, "rb") as fp:
        return pickle.load(fp)


class AlphabetCoder:
    """
    알파벳과 숫자를 인코딩/디코딩하는 클래스입니다.
    """

    @staticmethod
    def transform(text: str, encode: bool = True) -> str:
        """
        주어진 문자열의 각 문자를 변환합니다.
        소문자는 'a'에서 'z'까지 순환하며, 대문자는 'A'에서 'Z'까지 순환합니다.
        숫자는 '0'에서 '9'까지 순환합니다. 알파벳이나 숫자가 아닌 문자는 그대로 유지됩니다.
        encode가 True이면 인코딩, False이면 디코딩을 수행합니다.

        Args:
            text (str): 변환할 문자열
            encode (bool): 인코딩 여부 (기본값: True)

        Returns:
            str: 변환된 문자열
        """
        shift = 1 if encode else -1
        return ''.join(
            chr((ord(char) - ord('a') + shift) % 26 + ord('a')) if 'a' <= char <= 'z' else
            chr((ord(char) - ord('A') + shift) % 26 + ord('A')) if 'A' <= char <= 'Z' else
            chr((ord(char) - ord('0') + shift) % 10 + ord('0')) if '0' <= char <= '9' else
            char
            for char in text
        )

    @staticmethod
    def encode(text: str) -> str:
        """
        주어진 문자열을 인코딩합니다.

        Args:
            text (str): 변환할 문자열

        Returns:
            str: 인코딩된 문자열
        """
        return AlphabetCoder.transform(text, encode=True)

    @staticmethod
    def decode(text: str) -> str:
        """
        주어진 문자열을 디코딩합니다.

        Args:
            text (str): 변환할 문자열

        Returns:
            str: 디코딩된 문자열
        """
        return AlphabetCoder.transform(text, encode=False)

#######################
# date and time
#######################

Millisecond = 1.0 / 1000.0

#
# Timer
#
class Timer:
    """
    타이머 클래스
    """

    def __init__(self) -> None:
        """타이머 초기화"""
        self.reset()

    def reset(self) -> None:
        """타이머를 현재 시간으로 리셋"""
        self.begin = datetime.now()

    def check_passed(self, delta: timedelta) -> bool:
        """
        지정된 시간이 경과했는지 확인

        Args:
            delta (timedelta): 경과 시간

        Returns:
            bool: 지정된 시간이 경과했으면 True, 아니면 False
        """
        return delta < (datetime.now() - self.begin)

    @staticmethod
    def sleep(ms: int) -> None:
        """
        지정된 밀리초(ms) 동안 대기

        Args:
            ms (int): 대기할 시간(밀리초)
        """
        time.sleep(ms * Millisecond)

    @staticmethod
    def ms_to_datetime(ms: int) -> datetime:
        """
        밀리초(ms)를 datetime 객체로 변환

        Args:
            ms (int): 밀리초

        Returns:
            datetime: 변환된 datetime 객체
        """
        return datetime.fromtimestamp(ms * Millisecond)
    
    @property
    def now(self) -> datetime:
        """
        현재 시간을 반환

        Returns:
            datetime: 현재 시간
        """
        return datetime.now()
    
    @property
    def timestamp_ms(self) -> int:
        """
        현재 시간을 밀리초(ms) 타임스탬프로 반환

        Returns:
            int: 현재 시간의 밀리초 타임스탬프
        """
        return int(datetime.now().timestamp() / Millisecond)
    
    @property
    def uptime(self) -> timedelta:
        """
        타이머가 시작된 이후 경과된 시간을 반환

        Returns:
            timedelta: 경과된 시간
        """
        return datetime.now() - self.begin
    
    @property
    def elapsed_sec(self) -> float:
        """
        타이머가 시작된 이후 경과된 시간을 초 단위로 반환

        Returns:
            float: 경과된 시간(초)
        """
        return self.uptime.total_seconds()

#
# 함수
#
def get_timezone(zone: str = "Asia/Seoul") -> BaseTzInfo:
    """
    지정된 시간대 정보를 반환

    Args:
        zone (str): 시간대 (기본값: "Asia/Seoul")

    Returns:
        BaseTzInfo: 시간대 정보
    """
    return timezone(zone)


def gen_timestamp(fmt: str = "%Y%m%d%H%M%S%f") -> str:
    """
    현재 시간을 지정된 형식으로 반환

    Args:
        fmt (str): 시간 형식 (기본값: "%Y%m%d%H%M%S%f")

    Returns:
        str: 형식화된 현재 시간
    """
    tz = get_timezone()
    return datetime.now(tz).strftime(fmt)


def get_now(fmt: str = "%Y-%m-%d %H:%M:%S.%f", ofs: int = 3) -> str:
    """
    현재 시간을 지정된 형식으로 반환하고, 마지막 ofs 문자를 반환

    Args:
        fmt (str): 시간 형식 (기본값: "%Y-%m-%d %H:%M:%S.%f")
        ofs (int): 반환할 마지막 문자 수 (기본값: 3)

    Returns:
        str: 형식화된 현재 시간의 마지막 ofs 문자
    """
    return gen_timestamp(fmt)[-ofs]


def get_date_interval(after_days: int, date_format: str = "%Y%m%d") -> Tuple[str, str]:
    """
    지정된 일수 전후의 날짜를 반환

    Args:
        after_days (int): 기준 일수
        date_format (str): 날짜 형식 (기본값: "%Y-%m-%d")

    Returns:
        Tuple[str, str]: 시작 날짜와 종료 날짜
    """
    today = datetime.today()
    end = today.strftime(date_format)
    begin = (today - timedelta(days=after_days)).strftime(date_format)
    return begin, end


def check_expired(timestamp: str, elapsed_seconds: float) -> bool:
    """
    특정 시간이 경과되었으면 참, 아니면 거짓

    Args:
        timestamp (str): 기준 시간
        elapsed_seconds (float): 경과 시간(초)

    Returns:
        bool: 경과 시간이 지나면 True, 아니면 False
    """
    current_time = datetime.now()
    target_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S%f")
    time_difference = current_time - target_time
    print(f"{time_difference.total_seconds()} sec")
    return time_difference.total_seconds() > elapsed_seconds


def gen_date_to(target_date: str, fmt_str: str = "%Y%m%d") -> Generator[str, None, None]:
    """
    date string generator
    오늘부터 지정한 날짜 전일까지 날짜를 생성

    Args:
        target_date (str): 목표 날짜
        fmt_str (str): 날짜 형식 (기본값: "%Y%m%d")

    Yields:
        Generator[str, None, None]: 날짜 문자열
    """
    current_date = datetime.today()
    end_date = datetime.fromisoformat(target_date)
    
    while current_date > end_date:
        yield current_date.strftime(fmt_str)
        current_date -= timedelta(days=1)


def gen_date_past(n_days: int, fmt_str: str = "%Y%m%d") -> Generator[str, None, None]:
    """
    date string generator
    오늘부터 지정한 수의 날짜를 생성

    Args:
        n_days (int): 생성할 날짜 수
        fmt_str (str): 날짜 형식 (기본값: "%Y%m%d")

    Yields:
        Generator[str, None, None]: 날짜 문자열
    """
    current_date = datetime.today()
    end_date = current_date - timedelta(days=n_days)

    while current_date >= end_date:
        yield current_date.strftime(fmt_str)
        current_date -= timedelta(days=1)



#
# unittest
#
def unittest():
    uuid = gen_uuid()
    print(uuid)

    unique_key = gen_key()
    print(unique_key)

    # AlphabetCoder 테스트
    encoded = AlphabetCoder.encode("Hello123")
    print(f"Encoded: {encoded}")
    decoded = AlphabetCoder.decode(encoded)
    print(f"Decoded: {decoded}")
    
def unittest2():
    branch_name = get_git_branch()
    print(branch_name)

if __name__ == "__main__":
    from __init__ import print

    unittest()
    unittest2()
    print("done.")
