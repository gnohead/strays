#!python3
#-*- coding: utf-8 -*-

import websockets as wss
import asyncio
import json
import signal
import sys

class Socket(object):
    """
    웹소켓 연결을 관리하는 기본 클래스
    """

    def __init__(self, max_retries=5, retry_delay=2):
        """
        Socket 클래스의 생성자

        :param max_retries: 최대 재시도 횟수
        :param retry_delay: 재시도 간격 (초)
        """
        self.connected = False
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def connect(self, uri):
        """
        서버에 연결을 시도

        :param uri: 서버 URI
        """
        retries = 0

        while retries < self.max_retries:
            try:
                self.websocket = await wss.connect(uri)
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
        서버와의 연결을 종료
        """
        if self.connected:
            await self.websocket.close()
            self.connected = False
            print("Disconnected")

    async def send_message(self, message):
        """
        서버로 메시지를 전송

        :param message: 전송할 메시지
        """
        if self.connected:
            await self.websocket.send(json.dumps(message))

        else:
            print("Not connected")

    async def receive_message(self):
        """
        서버로부터 메시지를 수신

        :return: 수신한 메시지 (JSON 형식)
        """
        if self.connected:
            try:
                message = await self.websocket.recv()
                return json.loads(message)
            
            except wss.ConnectionClosedOK:
                print("Connection closed normally")
                return None
        else:
            print("Not connected")

    async def handle_error(self, error):
        """
        오류를 처리

        :param error: 발생한 오류
        """
        print(f"Error: {error}")


class Server(Socket):
    """
    웹소켓 서버를 관리하는 클래스
    """

    def __init__(self, host="localhost", port=8765, max_retries=5, retry_delay=2, message_handler=None):
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

    def set_message_handler(self, message_handler):
        """
        사용자 정의 메시지 핸들러를 설정

        :param message_handler: 사용자 정의 메시지 핸들러 함수
        """
        self.message_handler = message_handler

    async def process(self, websocket, path):
        """
        클라이언트로부터 메시지를 처리

        :param websocket: 웹소켓 객체
        :param path: 요청 경로
        """
        self.connected = True
        self.websocket = websocket  # websocket 설정

        try:
            async for message in websocket:
                print(f"Received message: {message}")
                response = self.message_handler(message)
                await self.send_message(response)

        except Exception as e:
            await self.handle_error(e)

        finally:
            self.connected = False
            self.websocket = None  # 연결 종료 시 websocket 해제

    def default_message_handler(self, message):
        """
        기본 메시지 핸들러

        :param message: 수신한 메시지
        :return: 처리된 메시지
        """
        return {"processed": message.upper()}

    async def start(self):
        """
        서버를 시작
        """
        self.server = await wss.serve(self.process, self.host, self.port)
        print(f"Server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def stop(self):
        """
        서버를 종료
        """
        self.server.close()
        await self.server.wait_closed()
        await self.disconnect()


class Client(Socket):
    """
    웹소켓 클라이언트를 관리하는 클래스
    """

    def __init__(self, uri="ws://localhost:8765", max_retries=5, retry_delay=2):
        """
        Client 클래스의 생성자

        :param uri: 서버 URI
        :param max_retries: 최대 재시도 횟수
        :param retry_delay: 재시도 간격 (초)
        """
        super().__init__(max_retries, retry_delay)
        self.uri = uri

    async def connect(self):
        """
        서버에 연결
        """
        await super().connect(self.uri)

    async def send_message(self, message):
        """
        서버로 메시지를 전송

        :param message: 전송할 메시지
        """
        await super().send_message(message)

    async def receive_message(self):
        """
        서버로부터 메시지를 수신

        :return: 수신한 메시지
        """
        response = await super().receive_message()

        if response:
            print(f"Received from server: {response}")
            
        return response

    async def start(self):
        """
        클라이언트를 시작
        """
        await self.connect()


async def setup_server_and_client(server, client):
    """
    서버와 클라이언트를 설정

    :param server: Server 객체
    :param client: Client 객체
    :return: 이벤트 루프, 서버 태스크, 클라이언트 태스크
    """
    loop = asyncio.get_event_loop()

    def shutdown():
        """
        종료 처리
        """
        print("Shutting down...")
        loop.create_task(server.stop())
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    server_task = loop.create_task(server.start())
    client_task = loop.create_task(client.start())

    return loop, server_task, client_task


#
# for unittest
#
async def unittest():
    """
    유닛 테스트 함수
    """
    def custom_message_handler(message):
        """
        사용자 정의 메시지 핸들러

        :param message: 수신한 메시지
        :return: 처리된 메시지
        """
        return {"custom_processed": message[::-1]}

    server = Server()
    client = Client()

    loop, server_task, client_task = await setup_server_and_client(server, client)

    await asyncio.sleep(1)
    server.set_message_handler(custom_message_handler)

    await asyncio.sleep(1)

    await client.send_message("hello!!")
    await asyncio.sleep(1)
    
    res = await client.receive_message()
    print(res)
    await client_task
    server_task.cancel()

    print("done.")


async def unittest2():
    """
    유닛 테스트 함수 2
    """
    server = Server()
    client = Client()

    loop, server_task, client_task = await setup_server_and_client(server, client)

    await asyncio.sleep(1)

    while True:
        message = input("Enter message to send to server (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        await client.send_message({"message": message})
        await client.receive_message()

    await client.disconnect()
    server_task.cancel()

    print("done.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'unittest2':
        asyncio.run(unittest2())
    else:
        asyncio.run(unittest())