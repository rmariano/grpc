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
"""Invocation-side implementation of gRPC Asyncio Python."""
import asyncio
from typing import Any, Optional, Sequence, Text

import grpc

from grpc import _common
from grpc._cython import cygrpc

from . import _base_call
from ._call import UnaryStreamCall, UnaryUnaryCall
from ._interceptor import (InterceptedUnaryUnaryCall,
                           UnaryUnaryClientInterceptor)
from ._typing import (ChannelArgumentType, DeserializingFunction, MetadataType,
                      SerializingFunction)
from ._utils import _timeout_to_deadline


class UnaryUnaryMultiCallable:
    """Factory an asynchronous unary-unary RPC stub call from client-side."""

    _channel: cygrpc.AioChannel
    _method: bytes
    _request_serializer: SerializingFunction
    _response_deserializer: DeserializingFunction
    _interceptors: Optional[Sequence[UnaryUnaryClientInterceptor]]
    _loop: asyncio.AbstractEventLoop

    def __init__(self, channel: cygrpc.AioChannel, method: bytes,
                 request_serializer: SerializingFunction,
                 response_deserializer: DeserializingFunction,
                 interceptors: Optional[Sequence[UnaryUnaryClientInterceptor]]
                ) -> None:
        self._loop = asyncio.get_event_loop()
        self._channel = channel
        self._method = method
        self._request_serializer = request_serializer
        self._response_deserializer = response_deserializer
        self._interceptors = interceptors

    def __call__(self,
                 request: Any,
                 *,
                 timeout: Optional[float] = None,
                 metadata: Optional[MetadataType] = None,
                 credentials: Optional[grpc.CallCredentials] = None,
                 wait_for_ready: Optional[bool] = None,
                 compression: Optional[grpc.Compression] = None
                ) -> _base_call.UnaryUnaryCall:
        """Asynchronously invokes the underlying RPC.

        Args:
          request: The request value for the RPC.
          timeout: An optional duration of time in seconds to allow
            for the RPC.
          metadata: Optional :term:`metadata` to be transmitted to the
            service-side of the RPC.
          credentials: An optional CallCredentials for the RPC. Only valid for
            secure Channel.
          wait_for_ready: This is an EXPERIMENTAL argument. An optional
            flag to enable wait for ready mechanism
          compression: An element of grpc.compression, e.g.
            grpc.compression.Gzip. This is an EXPERIMENTAL option.

        Returns:
          A Call object instance which is an awaitable object.

        Raises:
          RpcError: Indicating that the RPC terminated with non-OK status. The
            raised RpcError will also be a Call for the RPC affording the RPC's
            metadata, status code, and details.
        """
        if metadata:
            raise NotImplementedError("TODO: metadata not implemented yet")

        grpc_credentials = None
        if credentials is not None:
            grpc_credentials = credentials._credentials

        if wait_for_ready:
            raise NotImplementedError(
                "TODO: wait_for_ready not implemented yet")

        if compression:
            raise NotImplementedError("TODO: compression not implemented yet")

<<<<<<< HEAD
        if not self._interceptors:
            return UnaryUnaryCall(
                request,
                _timeout_to_deadline(timeout),
                self._channel,
                self._method,
                self._request_serializer,
                self._response_deserializer,
            )
        else:
            return InterceptedUnaryUnaryCall(
                self._interceptors,
                request,
                timeout,
                self._channel,
                self._method,
                self._request_serializer,
                self._response_deserializer,
            )
=======
        deadline = _timeout_to_deadline(self._loop, timeout)

        return UnaryUnaryCall(
            request,
            deadline,
            self._channel,
            self._method,
            self._request_serializer,
            self._response_deserializer,
            grpc_credentials,
        )
>>>>>>> Add support for credentials in the async unary call


class UnaryStreamMultiCallable:
    """Afford invoking a unary-stream RPC from client-side in an asynchronous way."""

    def __init__(self, channel: cygrpc.AioChannel, method: bytes,
                 request_serializer: SerializingFunction,
                 response_deserializer: DeserializingFunction) -> None:
        self._channel = channel
        self._method = method
        self._request_serializer = request_serializer
        self._response_deserializer = response_deserializer
        self._loop = asyncio.get_event_loop()

    def __call__(self,
                 request: Any,
                 *,
                 timeout: Optional[float] = None,
                 metadata: Optional[MetadataType] = None,
                 credentials: Optional[grpc.CallCredentials] = None,
                 wait_for_ready: Optional[bool] = None,
                 compression: Optional[grpc.Compression] = None
                ) -> _base_call.UnaryStreamCall:
        """Asynchronously invokes the underlying RPC.

        Args:
          request: The request value for the RPC.
          timeout: An optional duration of time in seconds to allow
            for the RPC.
          metadata: Optional :term:`metadata` to be transmitted to the
            service-side of the RPC.
          credentials: An optional CallCredentials for the RPC. Only valid for
            secure Channel.
          wait_for_ready: This is an EXPERIMENTAL argument. An optional
            flag to enable wait for ready mechanism
          compression: An element of grpc.compression, e.g.
            grpc.compression.Gzip. This is an EXPERIMENTAL option.

        Returns:
          A Call object instance which is an awaitable object.
        """
        if metadata:
            raise NotImplementedError("TODO: metadata not implemented yet")

        grpc_credentials = None
        if credentials is not None:
            grpc_credentials = credentials._credentials

        if wait_for_ready:
            raise NotImplementedError(
                "TODO: wait_for_ready not implemented yet")

        if compression:
            raise NotImplementedError("TODO: compression not implemented yet")

        deadline = _timeout_to_deadline(timeout)

        return UnaryStreamCall(
            request,
            deadline,
            self._channel,
            self._method,
            self._request_serializer,
            self._response_deserializer,
            grpc_credentials,
        )


class Channel:
    """Asynchronous Channel implementation.

    A cygrpc.AioChannel-backed implementation.
    """
    _channel: cygrpc.AioChannel
    _unary_unary_interceptors: Optional[Sequence[UnaryUnaryClientInterceptor]]

    def __init__(self, target: Text, options: Optional[ChannelArgumentType],
                 credentials: Optional[grpc.ChannelCredentials],
                 compression: Optional[grpc.Compression],
                 interceptors: Optional[Sequence[UnaryUnaryClientInterceptor]]):
        """Constructor.

        Args:
          target: The target to which to connect.
          options: Configuration options for the channel.
          credentials: A cygrpc.ChannelCredentials or None.
          compression: An optional value indicating the compression method to be
            used over the lifetime of the channel.
          interceptors: An optional list of interceptors that would be used for
            intercepting any RPC executed with that channel.
        """

<<<<<<< HEAD
        if credentials:
            raise NotImplementedError("TODO: credentials not implemented yet")
=======
        if options:
            raise NotImplementedError("TODO: options not implemented yet")
>>>>>>> Add support for credentials in the async unary call

        if compression:
            raise NotImplementedError("TODO: compression not implemented yet")

<<<<<<< HEAD
        if interceptors is None:
            self._unary_unary_interceptors = None
        else:
            self._unary_unary_interceptors = list(
                filter(
                    lambda interceptor: isinstance(interceptor,
                                                   UnaryUnaryClientInterceptor),
                    interceptors))

            invalid_interceptors = set(interceptors) - set(
                self._unary_unary_interceptors)

            if invalid_interceptors:
                raise ValueError(
                    "Interceptor must be "+\
                    "UnaryUnaryClientInterceptors, the following are invalid: {}"\
                    .format(invalid_interceptors))

        self._channel = cygrpc.AioChannel(_common.encode(target), options)
=======
        self._channel = cygrpc.AioChannel(_common.encode(target), credentials)
>>>>>>> Add support for credentials in the async unary call

    def unary_unary(
            self,
            method: Text,
            request_serializer: Optional[SerializingFunction] = None,
            response_deserializer: Optional[DeserializingFunction] = None
    ) -> UnaryUnaryMultiCallable:
        """Creates a UnaryUnaryMultiCallable for a unary-unary method.

        Args:
          method: The name of the RPC method.
          request_serializer: Optional behaviour for serializing the request
            message. Request goes unserialized in case None is passed.
          response_deserializer: Optional behaviour for deserializing the
            response message. Response goes undeserialized in case None
            is passed.

        Returns:
          A UnaryUnaryMultiCallable value for the named unary-unary method.
        """
        return UnaryUnaryMultiCallable(self._channel, _common.encode(method),
                                       request_serializer,
                                       response_deserializer,
                                       self._unary_unary_interceptors)

    def unary_stream(
            self,
            method: Text,
            request_serializer: Optional[SerializingFunction] = None,
            response_deserializer: Optional[DeserializingFunction] = None
    ) -> UnaryStreamMultiCallable:
        return UnaryStreamMultiCallable(self._channel, _common.encode(method),
                                        request_serializer,
                                        response_deserializer)

    def stream_unary(
            self,
            method: Text,
            request_serializer: Optional[SerializingFunction] = None,
            response_deserializer: Optional[DeserializingFunction] = None):
        """Placeholder method for stream-unary calls."""

    def stream_stream(
            self,
            method: Text,
            request_serializer: Optional[SerializingFunction] = None,
            response_deserializer: Optional[DeserializingFunction] = None):
        """Placeholder method for stream-stream calls."""

    async def _close(self):
        # TODO: Send cancellation status
        self._channel.close()

    async def __aenter__(self):
        """Starts an asynchronous context manager.

        Returns:
          Channel the channel that was instantiated.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Finishes the asynchronous context manager by closing gracefully the channel."""
        await self._close()

    async def close(self):
        """Closes this Channel and releases all resources held by it.

        Closing the Channel will proactively terminate all RPCs active with the
        Channel and it is not valid to invoke new RPCs with the Channel.

        This method is idempotent.
        """
        await self._close()
