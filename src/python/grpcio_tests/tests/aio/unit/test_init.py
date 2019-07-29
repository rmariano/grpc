import asyncio
import logging
import unittest

from grpc.experimental import aio


class TestInsecureChannel(unittest.TestCase):
    def setUp(self):
        aio.init_grpc_aio()

    def test_insecure_channel(self):
        async def coro():
            channel = aio.insecure_channel('target')
            self.assertIsInstance(channel, aio.Channel)

        asyncio.get_event_loop().run_until_complete(coro())


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
