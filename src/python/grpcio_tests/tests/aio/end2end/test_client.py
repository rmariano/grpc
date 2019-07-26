# Copyright 2019 gRPC authors.
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
import logging
import multiprocessing
import time
import unittest

from grpc.experimental import aio
from src.proto.grpc.testing import messages_pb2

# TODO: Change for an asynchronous server version once it's
# implemented.
class Server(multiprocessing.Process):
    """
    Synchronous server is executed in another process which initializes
    implicitly the grpc using the synchronous configuration. Both worlds
    can not coexist within the same process.
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
                return messages_pb2.SimpleResponse()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        add_TestServiceServicer_to_server(TestServiceServicer(), server)
        server.add_insecure_port('localhost:%d' % self.PORT)
        server.start()
        try:
            sleep(3600)
        finally:
            server.stop(None)


class TestClient(unittest.TestCase):
    def setUp(self):
        self._server = Server()
        self._server.start()
        # TODO(https://github.com/grpc/grpc/issues/19762) remove the sleep.
        time.sleep(0.1)
        aio.init_grpc_aio()

    def tearDown(self):
        self._server.terminate()

    def test_unary_unary(self):
        async def coro():
            channel = aio.insecure_channel('localhost:%d' % Server.PORT)
            hi = channel.unary_unary(
                '/grpc.testing.TestService/UnaryCall',
                request_serializer=messages_pb2.SimpleRequest.SerializeToString,
                response_deserializer=messages_pb2.SimpleResponse.FromString
            )
            response = await hi(messages_pb2.SimpleRequest())

            self.assertEqual(type(response), messages_pb2.SimpleResponse)

            await channel.close()

        asyncio.get_event_loop().run_until_complete(coro())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
