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
import multiprocessing
import time
import logging
import unittest

from grpc.experimental.aio import init_grpc_aio
from grpc.experimental.aio import insecure_channel
from src.proto.grpc.testing.messages_pb2 import SimpleRequest
from src.proto.grpc.testing.messages_pb2 import SimpleResponse

# TODO: Change for an asynchronous server version once it's
# implemented.
class Server(multiprocessing.Process):
    """
    Synchronous server is executed in another process which initializes
    implicitly the grpc using the synchronous configuration. Both worlds
    can not cohexist within the same process.
    """

    PORT = 3333

    def run(self):
        import grpc
        from time import sleep
        from concurrent import futures
        from src.proto.grpc.testing.test_pb2_grpc import add_TestServiceServicer_to_server
        from src.proto.grpc.testing.test_pb2_grpc import TestServiceServicer

        class TestServiceServicer(TestServiceServicer):
            def UnaryCall(self, request, context):
                return SimpleResponse()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        add_TestServiceServicer_to_server(TestServiceServicer(), server)
        server.add_insecure_port('localhost:%d' % self.PORT)
        server.start()
        while True:
            sleep(1)


class TestClient(unittest.TestCase):
    def setUp(self):
        self._server = Server()
        self._server.start()
        time.sleep(0.1)
        init_grpc_aio()

    def tearDown(self):
        self._server.terminate()

    def test_unary_unary(self):
        async def coro():
            channel = insecure_channel('localhost:%d' % Server.PORT)
            hi = channel.unary_unary(
                '/grpc.testing.TestService/UnaryCall',
                request_serializer=SimpleRequest.SerializeToString,
                response_deserializer=SimpleResponse.FromString
            )
            response = await hi(SimpleRequest())

            self.assertEqual(type(response), SimpleResponse)

            await channel.close()

        asyncio.get_event_loop().run_until_complete(coro())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
