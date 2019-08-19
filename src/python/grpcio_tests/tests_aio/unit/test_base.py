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

import asyncio
import unittest
import socket

from grpc.experimental import aio
from tests_aio.unit import sync_server


def _get_free_loopback_tcp_port():
    if socket.has_ipv6:
        tcp_socket = socket.socket(socket.AF_INET6)
    else:
        tcp_socket = socket.socket(socket.AF_INET)
    tcp_socket.bind(('', 0))
    address_tuple = tcp_socket.getsockname()
    return tcp_socket, "localhost:%s" % (address_tuple[1])


class AioTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._socket, cls._target = _get_free_loopback_tcp_port()
        cls._server = sync_server.Server(cls._target)
        cls._server.start()
        cls._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls._loop)
        aio.init_grpc_aio()

    @classmethod
    def tearDownClass(cls):
        cls._server.terminate()
        cls._socket.close()

    @property
    def loop(self):
        return self._loop

    @property
    def server_target(self):
        return self._target
