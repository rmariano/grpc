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
"""gRPC's Asynchronous Python API.

gRPC Async API objects may only be used on the thread on which they were
created. AsyncIO doesn't provide thread safety for most of its APIs.
"""
from typing import Any, Optional, Sequence, Text, Tuple

import grpc
from grpc._cython.cygrpc import init_grpc_aio

from ._base_call import RpcContext, Call, UnaryUnaryCall, UnaryStreamCall
from ._call import AioRpcError
from ._channel import Channel
from ._channel import UnaryUnaryMultiCallable

from ._interceptor import ClientCallDetails, UnaryUnaryClientInterceptor, InterceptedUnaryUnaryCall
from ._server import server, Server


def insecure_channel(
        target: Text,
        options: Optional[Sequence[Tuple[Text, Any]]] = None,
        compression: Optional[grpc.Compression] = None,
        interceptors: Optional[Sequence[UnaryUnaryClientInterceptor]] = None):
    """Creates an insecure asynchronous Channel to a server.

    Args:
      target: The server address
      options: An optional list of key-value pairs (channel args
        in gRPC Core runtime) to configure the channel.
      compression: An optional value indicating the compression method to be
        used over the lifetime of the channel. This is an EXPERIMENTAL option.
      interceptors: An optional sequence of interceptors that will be executed for
        any call executed with this channel.

    Returns:
      A Channel.
    """
    return Channel(target, () if options is None else options,
                   None,
                   compression,
                   interceptors=interceptors)


def secure_channel(target: Server,
                   credentials: grpc.ChannelCredentials,
                   options: Optional[list] = None,
                   compression: Optional[grpc.Compression] = None) -> Channel:
    """Creates a secure asynchronous Channel to a server.

    Args:
      target: The server address.
      credentials: A ChannelCredentials instance.
      options: An optional list of key-value pairs (channel args
        in gRPC Core runtime) to configure the channel.
      compression: An optional value indicating the compression method to be
        used over the lifetime of the channel. This is an EXPERIMENTAL option.

    Returns:
      An aio.Channel.
    """
    return Channel(target, () if options is None else options,
                   credentials._credentials, compression)


###################################  __all__  #################################

__all__ = ('AioRpcError', 'RpcContext', 'Call', 'UnaryUnaryCall',
           'UnaryStreamCall', 'init_grpc_aio', 'Channel',
           'UnaryUnaryMultiCallable', 'ClientCallDetails',
           'UnaryUnaryClientInterceptor', 'InterceptedUnaryUnaryCall',
           'insecure_channel', 'secure_channel', 'server', 'Server')
