import asyncio
import logging
import unittest

from unittest.mock import MagicMock, patch

from grpc.experimental import aio


class TestChannel(unittest.TestCase):
    def test_unary_unary(self):
        async def coro():
            channel = aio.insecure_channel('target:port')
            self.assertIsInstance(
                channel.unary_unary('/grpc.testing.TestService/UnaryCall'),
                aio.UnaryUnaryMultiCallable
            )

        with patch("grpc._cython.cygrpc"):
            asyncio.get_event_loop().run_until_complete(coro())


class TestUnaryUnaryMultiCallable(unittest.TestCase):
    def test_call(self):
        async def coro():
            channel = aio.insecure_channel('target:port')
            multicallable = channel.unary_unary('/grpc.testing.TestService/UnaryCall')
            multicallable._channel = MagicMock()
            async def unary_unary(*args, **kwargs):
                return 'world'
            multicallable._channel.unary_unary = MagicMock(wraps=unary_unary)

            response = await multicallable(b'hello')
            self.assertEqual(response, 'world')
            multicallable._channel.unary_unary.assert_called_once_with(b'/grpc.testing.TestService/UnaryCall', b'hello')

        with patch("grpc._cython.cygrpc"):
            asyncio.get_event_loop().run_until_complete(coro())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main(verbosity=2)
