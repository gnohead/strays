#!python
#-*- coding: utf-8 -*- 

import time
from datetime import datetime, timedelta
from pytz import timezone
from typing import Generator, Any, Tuple

Millisecond = 1.0 / 1000.0

#
# Timer
#
class Timer(object):

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self.begin = datetime.now()

    def check_passed(self, delta:timedelta) -> bool:
        return delta < (datetime.now() - self.begin)

    @staticmethod
    def sleep(ms:int):
        time.sleep(ms * Millisecond)

    @staticmethod
    def ms_to_datetime(ms:int) -> datetime:
        return datetime.fromtimestamp(ms * Millisecond)
    
    @property
    def now(self) -> datetime:
        return datetime.now()
    
    @property
    def timestamp_ms(self) -> int:
        return int(datetime.now().timestamp() / Millisecond)
    
    @property
    def uptime(self) -> timedelta:
        return (datetime.now() - self.begin)
    
    @property
    def elapsed_sec(self) -> float:
        return self.uptime.total_seconds()

#
# 함수
#
def get_timestamp() -> str:
    """
    TimeStamp 생성기
    """
    tz = timezone('Asia/Seoul')
    return datetime.now(tz).strftime("%Y%m%d%H%M%S%f")


def get_date_interval(after_days:int, date_format:str="%Y-%m-%d") -> Tuple[str, str]:
    today = datetime.today()

    end = today.strftime(date_format)
    begin = (today - timedelta(days=after_days)).strftime(date_format)
    
    return (begin, end)


def check_expired(timestamp:str, elapsed_seconds:float) -> bool:
    """
    특정 시간이 경과되었으면 참, 아니면 거짓
    """
    current_time = datetime.now()
    target_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S%f")
    time_difference = current_time - target_time
    print(f"{time_difference.total_seconds()} sec")
    return time_difference.total_seconds() > elapsed_seconds


def gen_date_to(target_date:str, fmt_str:str="%Y%m%d") -> Generator[Any, None, None]:
    """
    date string generator
    오늘부터 지정한 날짜 전일까지 날짜를 생성
    """
    current_date = datetime.today()
    end_date = datetime.fromisoformat(target_date)
    
    while current_date > end_date:
        yield current_date.strftime(fmt_str)
        current_date -= timedelta(days=1)


def gen_date_past(n_days:int, fmt_str:str="%Y%m%d") -> Generator[Any, None, None]:
    """
    date string generator
    오늘부터 지정한 수의 날짜를 생성
    """
    current_date = datetime.today()
    end_date = current_date - timedelta(days=n_days)

    while current_date >= end_date:
        yield current_date.strftime(fmt_str)
        current_date -= timedelta(days=1)


#
# unittest()
#
def unittest():
    ts = get_timestamp()
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