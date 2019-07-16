# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import subprocess
import time
import logging
import unittest

from grpc.experimental.aio import init_grpc_aio
from grpc.experimental.aio import insecure_channel

from proto import echo_pb2


class Server:
    """
    TODO: Change for the asynchronous server version.

    Synchronous server runs in another process which initializes
    implicitly the grpc using the synchronous configuration.
    Both worlds can not cohexist within the same process.
    """
    def __init__(self):
        self._process = None

    def start(self):
        return
        assert not self._process

        self._process = subprocess.Popen(
            ["python", "src/python/grpcio_tests/tests/asyncio/end2end/sync_server.py"],
            env=None
        )

        # giving some time for starting the server
        time.sleep(1)

    def stop(self):
        return
        self._process.terminate()


class TestClient(unittest.TestCase):
    def setUp(self):
        grpc_init_asyncio()
        self._server = Server()
        self._server.start()

    def tearDown(self):
        self._server.stop()

    def test_unary_unary(self):
        async def coro():
            channel = insecure_channel('localhost:3333')
            hi = channel.unary_unary(
                '/echo.Echo/Hi',
                request_serializer=echo_pb2.EchoRequest.SerializeToString,
                response_deserializer=echo_pb2.EchoReply.FromString
            )
            response = await hi(echo_pb2.EchoRequest(message="Hi Grpc Asyncio"))

            assert response.message == "Hi Grpc Asyncio"

            channel.close()

        asyncio.get_event_loop().run_until_complete(coro())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
