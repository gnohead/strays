#!python3
#-*- coding: utf-8 -*-

import websockets as wss
import asyncio
import signal
import sys
from abc import abstractmethod

from typing import Union, Dict, Optional

class Socket(object):
    """
    WebSocket 연결을 관리하는 기본 클래스
    """

    def __init__(self, max_retries:int=5, retry_delay:int=2):
        """
        Socket 클래스의 생성자

        :param max_retries: 최대 재시도 횟수
        :param retry_delay: 재시도 간격 (초)
        """
        self.connected = False
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def connect(self, uri:str, extra_headers:Optional[Dict[str, str]]=None):
        """
        서버에 연결을 시도합니다.

        :param uri: 서버 URI
        :param extra_headers: 추가 헤더
        """
        retries = 0

        while retries < self.max_retries:
            try:
                self.websocket = await wss.connect(uri, extra_headers=extra_headers)
                self.connected = True
                print("Connected")
                return
            
            except Exception as e:
                print(f"Connection failed: {e}")
                retries += 1
                print(f"Retrying... ({retries}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)

        print("Failed to connect after maximum retries")

    async def disconnect(self):
        """
        서버와의 연결을 종료합니다.
        """
        if self.connected:
            await self.websocket.close()
            self.connected = False
            print("Disconnected")

    async def send(self, message:Union[str, bytes], timeout:Optional[float]=None):
        """
        서버로 메시지를 전송합니다.

        :param message: 전송할 메시지
        :param timeout: 타임아웃 시간 (초)
        """
        if self.connected:
            try:
                await asyncio.wait_for(self.websocket.send(message), timeout)
            except asyncio.TimeoutError:
                print("Send message timed out")
        else:
            print("Not connected")

    async def receive(self, timeout:Optional[float]=None):
        """
        서버로부터 메시지를 수신합니다.

        :param timeout: 타임아웃 시간 (초)
        :return: 수신한 메시지
        """
        if self.connected:
            try:
                return await asyncio.wait_for(self.websocket.recv(), timeout)
            except asyncio.TimeoutError:
                print("Receive message timed out")
                return None
            except wss.ConnectionClosedOK:
                print("Connection closed normally")
                return None
            except Exception as e:
                await self.handle_error(e)
                return None
        else:
            print("Not connected")

    async def handle_error(self, error:Exception):
        """
        오류를 처리합니다.

        :param error: 발생한 오류
        """
        print(f"Error: {error}")

    async def setup(self, *args, **kwargs) -> tuple:
        """
        소켓을 설정합니다.

        :param args: start 메서드에 전달할 위치 인수
        :param kwargs: start 메서드에 전달할 키워드 인수
        :return: 이벤트 루프, 소켓 태스크
        """
        loop = asyncio.get_running_loop()

        async def shutdown():
            """
            종료 처리
            """
            print("Shutting down...")
            if isinstance(self, (Server, Client)):
                await self.stop()
                
            loop.stop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

        task = loop.create_task(self.start(*args, **kwargs))

        return loop, task
    
    @abstractmethod
    async def start(self, *args, **kwargs):
        pass

    def __aiter__(self):
        """
        비동기 이터레이터를 반환합니다.
        """
        return self

    async def __anext__(self):
        """
        비동기 이터레이터의 다음 항목을 반환합니다.
        """
        if not self.connected:
            raise StopAsyncIteration

        message = await self.receive(timeout=1.0)
        if message is None:
            raise StopAsyncIteration

        return message


class Server(Socket):
    """
    WebSocket 서버를 관리하는 클래스
    """

    def __init__(self, host:str="localhost", port:int=8765, max_retries:int=5, retry_delay:int=2, message_handler:Optional[callable]=None):
        """
        Server 클래스의 생성자

        :param host: 서버 호스트
        :param port: 서버 포트
        :param max_retries: 최대 재시도 횟수
        :param retry_delay: 재시도 간격 (초)
        :param message_handler: 사용자 정의 메시지 핸들러
        """
        super().__init__(max_retries, retry_delay)
        self.host = host
        self.port = port
        self.message_handler = message_handler if message_handler else self.default_message_handler

    def set_message_handler(self, message_handler:callable):
        """
        사용자 정의 메시지 핸들러를 설정합니다.

        :param message_handler: 사용자 정의 메시지 핸들러 함수
        """
        self.message_handler = message_handler

    async def process(self, websocket:wss.WebSocketServerProtocol, path:str):
        """
        클라이언트로부터 메시지를 처리합니다.

        :param websocket: 웹소켓 객체
        :param path: 요청 경로
        """
        self.connected = True
        self.websocket = websocket  # websocket 설정

        try:
            async for message in websocket:
                print(f"Received message: {message}")
                response = self.message_handler(message)
                await self.send(response)

        except Exception as e:
            await self.handle_error(e)

        finally:
            self.connected = False
            self.websocket = None  # 연결 종료 시 websocket 해제

    def default_message_handler(self, message:str) -> bytes:
        """
        기본 메시지 핸들러

        :param message: 수신한 메시지
        :return: 처리된 메시지
        """
        import json
        return json.dumps({"processed": message.upper()}).encode(encoding="utf-8")

    async def start(self):
        """
        서버를 시작합니다.
        """
        self.server = await wss.serve(self.process, self.host, self.port)
        print(f"Server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def stop(self):
        """
        서버를 종료합니다.
        """
        self.server.close()
        await self.server.wait_closed()
        await self.disconnect()


class Client(Socket):
    """
    WebSocket 클라이언트를 관리하는 클래스
    """

    def __init__(self, uri:str, max_retries:int=5, retry_delay:int=2):
        """
        Client 클래스의 생성자

        :param uri: 서버 URI
        :param max_retries: 최대 재시도 횟수
        :param retry_delay: 재시도 간격 (초)
        """
        super().__init__(max_retries, retry_delay)
        self.uri = uri

    async def connect(self, extra_headers:Optional[Dict[str, str]]=None):
        """
        서버에 연결합니다.
        """
        await super().connect(self.uri, extra_headers=extra_headers)

    async def send(self, message:str, timeout:Optional[int]=None):
        """
        서버로 메시지를 전송합니다.

        :param message: 전송할 메시지
        :param timeout: 타임아웃 시간 (초)
        """
        await super().send(message, timeout)

    async def receive(self, timeout:Optional[int]=None):
        """
        서버로부터 메시지를 수신합니다.

        :param timeout: 타임아웃 시간 (초)
        :return: 수신한 메시지
        """
        response = await super().receive(timeout)

        if response:
            print(f"Received from server: {response}")
            
        return response

    async def start(self, extra_headers:Optional[Dict[str, str]]=None):
        """
        클라이언트를 시작합니다.
        """
        await self.connect(extra_headers=extra_headers)


#
# for unittest
#
async def unittest():
    """
    유닛 테스트 함수
    """
    def custom_message_handler(message:str) -> bytes:
        """
        사용자 정의 메시지 핸들러

        :param message: 수신한 메시지
        :return: 처리된 메시지
        """
        import json
        return json.dumps({"custom_processed": message.upper()}).encode(encoding="utf-8")

    server = Server()
    client = Client(uri="ws://localhost:8765")

    loop_server, server_task = await server.setup()
    loop_client, client_task = await client.setup()

    await asyncio.sleep(1)
    server.set_message_handler(custom_message_handler)

    await asyncio.sleep(1)

    await client.send("hello!!")
    await asyncio.sleep(1)
    
    res = await client.receive()
    print(res)
    
    await client.disconnect()
    server_task.cancel()

    print("done.")


async def unittest2():
    """
    유닛 테스트 함수 2
    """
    server = Server()
    client = Client(uri="ws://localhost:8765")

    loop_server, server_task = await server.setup()
    loop_client, client_task = await client.setup()

    await asyncio.sleep(1)

    while True:
        message = input("Enter message to send to server (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        await client.send(message)
        await client.receive()

    await client.disconnect()
    server_task.cancel()

    print("done.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'unittest2':
        asyncio.run(unittest2())
    else:
        asyncio.run(unittest())