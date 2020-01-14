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


cdef class AioChannel:
    def __cinit__(self, bytes target, tuple options, ChannelCredentials credentials=None):
        if options is None:
            options = ()
        cdef _ChannelArgs channel_args = _ChannelArgs(options)
        self._target = target
        self.cq = CallbackCompletionQueue()

        if credentials is None:
            self.channel = grpc_insecure_channel_create(<char *>target, channel_args.c_args(), NULL)
            self._is_secure = False
        else:
            self.channel = grpc_secure_channel_create(
                <grpc_channel_credentials *> credentials.c(),
                <char *> target,
                channel_args.c_args(),
                NULL
            )
            self._is_secure = True

    def __repr__(self):
        class_name = self.__class__.__name__
        id_ = id(self)
        return f"<{class_name} {id_}>"

    def close(self):
        grpc_channel_destroy(self.channel)

    def call(self,
             bytes method,
             object deadline,
             CallCredentials call_credentials):
        """Assembles a Cython Call object.

        Returns:
          The _AioCall object.
        """
        if call_credentials is not None and not self._is_secure:
            raise RuntimeError("Cannot provide call credentials to an insecure channel.")
        cdef _AioCall call = _AioCall(self, deadline, method, call_credentials)
        return call
