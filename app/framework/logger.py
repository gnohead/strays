#!python3
#-*- coding: utf-8 -*-

#
# Author: gnohead
# Created: 2024. 5.
# Modified: 2024. 12.
# 

"""
logger

- 콘솔과 파일에 로그를 출력
- print() 함수를 대체하여 편하게 로그를 기록하기 위함
- IceCreamDebugger 도입!
"""

import logging

from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pytz import timezone

from icecream import install, ic, IceCreamDebugger


#
# 로거 오브젝트 설정을 위한 요소
#
class LocalTimeFormatter(logging.Formatter):
    converter = timezone('Asia/Seoul')
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.converter)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime(self.default_time_format)
            s = f"{t},{record.msecs:03d}"
        return s


def create_logger(logfolderpath:str, name:str):
    # 로그 폴더 생성
    Path(logfolderpath).mkdir(parents=True, exist_ok=True)

    # 포맷터 설정; 로그의 출력 형식을 지정
    log_format = "%(asctime)s.%(msecs)03d|> %(message)s"
    formatter = LocalTimeFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 파일 핸들러; 로그 파일의 크기를 10MB로 제한하고 백업 파일 5개를 유지
    file_handler = RotatingFileHandler(f"{logfolderpath}/{name}.log", maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # 로거 가져오기
    logging.basicConfig(
        level=logging.DEBUG,
        handlers= [
            console_handler,
            file_handler
        ]
    )

    return logging.getLogger(name)


def get_logger() -> IceCreamDebugger:
    from configurations import load
    
    configs = load()
    logpath = configs.path.log
    appname = configs.attributes.appname

    # 로거 오브젝트 생성
    log_printer = create_logger(logpath, appname)

    install()    
    ic.configureOutput(prefix="\n", outputFunction=log_printer.info)
    return ic


#
# unittest
# 
def unittest():
    print = get_logger()
    print("abc")
    print()
    
    def test(text:str) -> str:
        return "_".join(text)
    
    A = "AAA"
    res = test(print(A))
    print(res)


if __name__ == "__main__":
    unittest()
    print("done.")
