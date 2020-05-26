# Copyright 2020 The gRPC Authors
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
import grpc
from grpc.experimental import aio
from grpc.experimental.aio._typing import MetadataType, MetadatumType, MetadataKey, MetadataValue

from tests.unit.framework.common import test_constants


def seen_metadata(expected: MetadataType, actual: MetadataType):
    return not bool(set(tuple(expected)) - set(tuple(actual)))


def seen_metadatum(expected_key: MetadataKey, expected_value: MetadataValue,
                   actual: MetadataType) -> bool:
    obtained = actual[expected_key]
    return obtained == expected_value


async def block_until_certain_state(channel: aio.Channel,
                                    expected_state: grpc.ChannelConnectivity):
    state = channel.get_state()
    while state != expected_state:
        await channel.wait_for_state_change(state)
        state = channel.get_state()


def inject_callbacks(call):
    first_callback_ran = asyncio.Event()

    def first_callback(call):
        # Validate that all resopnses have been received
        # and the call is an end state.
        assert call.done()
        first_callback_ran.set()

    second_callback_ran = asyncio.Event()

    def second_callback(call):
        # Validate that all responses have been received
        # and the call is an end state.
        assert call.done()
        second_callback_ran.set()

    call.add_done_callback(first_callback)
    call.add_done_callback(second_callback)

    async def validation():
        await asyncio.wait_for(
            asyncio.gather(first_callback_ran.wait(),
                           second_callback_ran.wait()),
            test_constants.SHORT_TIMEOUT)

    return validation()
