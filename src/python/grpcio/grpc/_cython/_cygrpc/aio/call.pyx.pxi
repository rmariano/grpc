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

cimport cpython

_EMPTY_FLAGS = 0
_EMPTY_METADATA = ()


cdef class _AioCall:

    _OP_ARRAY_LENGTH = 6

    def __cinit__(self, AioChannel channel):
        self._channel = channel
        self._functor.functor_run = _AioCall.functor_run

        self._cq = grpc_completion_queue_create_for_callback(
            <grpc_experimental_completion_queue_functor *> &self._functor,
            NULL
        )

        self._watcher_call.functor.functor_run = _AioCall.watcher_call_functor_run
        self._watcher_call.obj = <cpython.PyObject *> self
        self._waiter_call = None

    def __dealloc__(self):
        grpc_completion_queue_shutdown(self._cq)
        grpc_completion_queue_destroy(self._cq)

    def __repr__(self):
        class_name = self.__class__.__name__
        id_ = id(self)
        return f"<{class_name} {id_}>"

    @staticmethod
    cdef void functor_run(grpc_experimental_completion_queue_functor* functor, int succeed):
        pass

    @staticmethod
    cdef void watcher_call_functor_run(grpc_experimental_completion_queue_functor* functor, int succeed):
        call = <_AioCall>(<CallbackContext *>functor).obj

        assert call._waiter_call

        if succeed == 0:
            call._waiter_call.set_exception(Exception("Some error ocurred"))
        else:
            call._waiter_call.set_result(None)

    async def unary_unary(self, method, request):
        cdef grpc_call * call
        cdef grpc_slice method_slice
        cdef grpc_op * ops

        cdef Operation initial_metadata_operation
        cdef Operation send_message_operation
        cdef Operation send_close_from_client_operation
        cdef Operation receive_initial_metadata_operation
        cdef Operation receive_message_operation
        cdef Operation receive_status_on_client_operation

        cdef tuple all_operations

        cdef grpc_call_error call_status


        method_slice = grpc_slice_from_copied_buffer(
            <const char *> method,
            <size_t> len(method)
        )

        call = grpc_channel_create_call(
            self._channel.channel,
            NULL,
            0,
            self._cq,
            method_slice,
            NULL,
            _timespec_from_time(None),
            NULL
        )

        grpc_slice_unref(method_slice)

        ops = <grpc_op *>gpr_malloc(sizeof(grpc_op) * self._OP_ARRAY_LENGTH)

        initial_metadata_operation = SendInitialMetadataOperation(_EMPTY_METADATA, GRPC_INITIAL_METADATA_USED_MASK)
        send_message_operation = SendMessageOperation(request, _EMPTY_FLAGS)
        send_close_from_client_operation = SendCloseFromClientOperation(_EMPTY_FLAGS)
        receive_initial_metadata_operation = ReceiveInitialMetadataOperation(_EMPTY_FLAGS)
        receive_message_operation = ReceiveMessageOperation(_EMPTY_FLAGS)
        receive_status_on_client_operation = ReceiveStatusOnClientOperation(_EMPTY_FLAGS)

        all_operations = (
            initial_metadata_operation,
            send_message_operation,
            send_close_from_client_operation,
            receive_initial_metadata_operation,
            receive_message_operation,
            receive_status_on_client_operation
        )
        cdef int idx = 0
        for operation in all_operations:
            operation.c()
            ops[idx] = <grpc_op> operation.c_op
            idx += 1

        self._waiter_call = asyncio.get_running_loop().create_future()

        call_status = grpc_call_start_batch(
            call,
            ops,
            self._OP_ARRAY_LENGTH,
            &self._watcher_call.functor,
            NULL
        )

        try:
            if call_status != GRPC_CALL_OK:
                self._waiter_call = None
                raise Exception("Error with grpc_call_start_batch {}".format(call_status))

            await self._waiter_call

        finally:

            for operation in all_operations:
                operation.un_c()

            grpc_call_unref(call)
            gpr_free(ops)

            return receive_message_operation.message()
