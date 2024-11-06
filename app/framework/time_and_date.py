#!python
#-*- coding: utf-8 -*- 

import time
from datetime import datetime, timedelta
from pytz import timezone, BaseTzInfo
from typing import Generator, Any, Tuple

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
# unittest()
#
def unittest() -> None:
    """유닛 테스트 함수"""
    ts = gen_timestamp()
    print(ts)

    timer = Timer()

    intvl = timedelta(seconds=2.0)
    while not timer.check_passed(intvl):
        timer.sleep(1)
        print(timer.elapsed_sec)
        # print(timer.now)
        tsms = timer.timestamp_ms
        print(timer.ms_to_datetime(tsms))

    print("done")

if __name__ == "__main__":
    unittest()
    print("done.")