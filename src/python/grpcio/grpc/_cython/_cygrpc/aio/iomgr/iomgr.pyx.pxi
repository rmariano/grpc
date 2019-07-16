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
from cpython cimport Py_INCREF, Py_DECREF

from libc cimport string


cdef grpc_socket_vtable asyncio_socket_vtable
cdef grpc_custom_resolver_vtable asyncio_resolver_vtable
cdef grpc_custom_timer_vtable asyncio_timer_vtable
cdef grpc_custom_poller_vtable asyncio_pollset_vtable


cdef grpc_error* asyncio_socket_init(
        grpc_custom_socket* g_socket,
        int domain) with gil:
    socket = _AsyncioSocket.create(g_socket)
    Py_INCREF(socket)
    g_socket.impl = <void*>socket
    return <grpc_error*>0


cdef void asyncio_socket_destroy(grpc_custom_socket* g_socket) with gil:
    Py_DECREF(<_AsyncioSocket>g_socket.impl)


cdef void asyncio_socket_connect(
        grpc_custom_socket* g_socket,
        const grpc_sockaddr* g_addr,
        size_t addr_len,
        grpc_custom_connect_callback g_connect_cb) with gil:

    host, port = sockaddr_to_tuple(g_addr, addr_len)
    socket = <_AsyncioSocket>g_socket.impl
    socket.connect(host, port, g_connect_cb)


cdef void asyncio_socket_close(
        grpc_custom_socket* g_socket,
        grpc_custom_close_callback g_close_cb) with gil:
    socket = (<_AsyncioSocket>g_socket.impl)
    if socket.is_connected():
        socket.writer.close()
    g_close_cb(g_socket)


cdef void asyncio_socket_shutdown(grpc_custom_socket* g_socket) with gil:
    raise NotImplemented()


cdef void asyncio_socket_write(
        grpc_custom_socket* g_socket,
        grpc_slice_buffer* g_slice_buffer,
        grpc_custom_write_callback g_write_cb) with gil:
    socket = (<_AsyncioSocket>g_socket.impl)
    socket.write(g_slice_buffer, g_write_cb)


cdef void asyncio_socket_read(
        grpc_custom_socket* g_socket,
        char* buffer_,
        size_t length,
        grpc_custom_read_callback g_read_cb) with gil:
    socket = (<_AsyncioSocket>g_socket.impl)
    socket.read(buffer_, length, g_read_cb)


cdef grpc_error* asyncio_socket_getpeername(
        grpc_custom_socket* g_socket,
        const grpc_sockaddr* g_addr,
        int* length) with gil:
    raise NotImplemented()


cdef grpc_error* asyncio_socket_getsockname(
        grpc_custom_socket* g_socket,
        const grpc_sockaddr* g_addr,
        int* length) with gil:
    raise NotImplemented()


cdef grpc_error* asyncio_socket_listen(grpc_custom_socket* g_socket) with gil:
    raise NotImplemented()


cdef grpc_error* asyncio_socket_bind(
        grpc_custom_socket* g_socket,
        const grpc_sockaddr* g_addr,
        size_t len, int flags) with gil:
    raise NotImplemented()


cdef void asyncio_socket_accept(
        grpc_custom_socket* g_socket,
        grpc_custom_socket* g_socket_client,
        grpc_custom_accept_callback g_accept_cb) with gil:
    raise NotImplemented()


cdef grpc_error* asyncio_resolve(
        char* host,
        char* port,
        grpc_resolved_addresses** res) with gil:
    raise NotImplemented()


cdef void asyncio_resolve_async(
        grpc_custom_resolver* g_resolver,
        char* host,
        char* port) with gil:
    resolver = _AsyncioResolver.create(g_resolver)
    resolver.resolve(host, port)


cdef void asyncio_timer_start(grpc_custom_timer* t) with gil:
    timer = _AsyncioTimer.create(t, t.timeout_ms / 1000.0)
    Py_INCREF(timer)
    t.timer = <void*>timer


cdef void asyncio_timer_stop(grpc_custom_timer* t) with gil:
    timer = <_AsyncioTimer>t.timer
    timer.stop()
    Py_DECREF(timer)


cdef void asyncio_init_loop() with gil:
    pass


cdef void asyncio_destroy_loop() with gil:
    pass


cdef void asyncio_kick_loop() with gil:
    pass


cdef void asyncio_run_loop(size_t timeout_ms) with gil:
    pass


def init_grpc_aio():

    asyncio_resolver_vtable.resolve = asyncio_resolve
    asyncio_resolver_vtable.resolve_async = asyncio_resolve_async

    asyncio_socket_vtable.init = asyncio_socket_init
    asyncio_socket_vtable.connect = asyncio_socket_connect
    asyncio_socket_vtable.destroy = asyncio_socket_destroy
    asyncio_socket_vtable.shutdown = asyncio_socket_shutdown
    asyncio_socket_vtable.close = asyncio_socket_close
    asyncio_socket_vtable.write = asyncio_socket_write
    asyncio_socket_vtable.read = asyncio_socket_read
    asyncio_socket_vtable.getpeername = asyncio_socket_getpeername
    asyncio_socket_vtable.getsockname = asyncio_socket_getsockname
    asyncio_socket_vtable.bind = asyncio_socket_bind
    asyncio_socket_vtable.listen = asyncio_socket_listen
    asyncio_socket_vtable.accept = asyncio_socket_accept

    asyncio_timer_vtable.start = asyncio_timer_start
    asyncio_timer_vtable.stop = asyncio_timer_stop

    asyncio_pollset_vtable.init = asyncio_init_loop
    asyncio_pollset_vtable.poll = asyncio_run_loop
    asyncio_pollset_vtable.kick = asyncio_kick_loop
    asyncio_pollset_vtable.shutdown = asyncio_destroy_loop

    grpc_custom_iomgr_init(
        &asyncio_socket_vtable,
        &asyncio_resolver_vtable,
        &asyncio_timer_vtable,
        &asyncio_pollset_vtable
    )
    grpc_init()
