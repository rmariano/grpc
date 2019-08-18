# Copyright 2019 The gRPC Authors.
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

import logging
import unittest

from grpc.experimental import aio
from src.proto.grpc.testing import messages_pb2
from tests_aio.unit import test_base


class TestChannel(test_base.AioTestBase):

    def test_async_context(self):

        async def coro():
            async with aio.insecure_channel(self.server_target) as channel:
                hi = channel.unary_unary(
                    '/grpc.testing.TestService/UnaryCall',
                    request_serializer=messages_pb2.SimpleRequest.
                    SerializeToString,
                    response_deserializer=messages_pb2.SimpleResponse.FromString
                )
                await hi(messages_pb2.SimpleRequest())

        self.loop.run_until_complete(coro())

    def test_unary_unary(self):

        async def coro():
            channel = aio.insecure_channel(self.server_target)
            hi = channel.unary_unary(
                '/grpc.testing.TestService/UnaryCall',
                request_serializer=messages_pb2.SimpleRequest.SerializeToString,
                response_deserializer=messages_pb2.SimpleResponse.FromString)
            response = await hi(messages_pb2.SimpleRequest())

            self.assertEqual(type(response), messages_pb2.SimpleResponse)

            await channel.close()

        self.loop.run_until_complete(coro())

    def test_unary_call_survives_timeout(self):
        """When time(call) <= timeout ==> continue normally"""
        async def coro():
            channel = aio.insecure_channel(self.server_target)
            hello_call = channel.unary_unary(
                "/grpc.testing.TestService/EmptyCall",
                request_serializer=messages_pb2.SimpleRequest.SerializeToString,
                response_deserializer=messages_pb2.SimpleResponse.FromString
            )
            response = await hello_call(messages_pb2.SimpleRequest(), timeout=0.5)
            await channel.close()

            self.assertEqual(response.username, "test-timeout")

        self.loop.run_until_complete(coro())

    def test_unary_call_times_out(self):
        """When time(call) > timeout ==> cancel"""
        async def coro():
            channel = aio.insecure_channel(self.server_target)
            empty_call_with_sleep = channel.unary_unary(
                "/grpc.testing.TestService/EmptyCall",
                request_serializer=messages_pb2.SimpleRequest.SerializeToString,
                response_deserializer=messages_pb2.SimpleResponse.FromString,
            )
            await empty_call_with_sleep(messages_pb2.SimpleRequest(), timeout=0.1)
            await channel.close()

        self.loop.run_until_complete(coro())


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
