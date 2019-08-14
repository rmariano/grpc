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

from grpc.experimental import aio
from tests_aio.unit import sync_server


class AioTestBase(unittest.TestCase):

    def setUp(self):
        self._server = sync_server.Server()
        self._server.start()
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        aio.init_grpc_aio()

    def tearDown(self):
        self._server.terminate()

    @property
    def loop(self):
        return self._loop

    @property
    def server_target(self):
        return 'localhost:%d' % sync_server.Server.PORT
