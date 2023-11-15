    def sendall(self, data, flags=0):
        if isinstance(data, unicode):
            data = data.encode()
        # this sendall is also reused by gevent.ssl.SSLSocket subclass,
        # so it should not call self._sock methods directly
        data_memory = _get_memory(data)
        len_data_memory = len(data_memory)
        if not len_data_memory:
            # Don't send empty data, can cause SSL EOFError.
            # See issue 719
            return 0

        # On PyPy up through 2.6.0, subviews of a memoryview() object
        # copy the underlying bytes the first time the builtin
        # socket.send() method is called. On a non-blocking socket
        # (that thus calls socket.send() many times) with a large
        # input, this results in many repeated copies of an ever
        # smaller string, depending on the networking buffering. For
        # example, if each send() can process 1MB of a 50MB input, and
        # we naively pass the entire remaining subview each time, we'd
        # copy 49MB, 48MB, 47MB, etc, thus completely killing
        # performance. To workaround this problem, we work in
        # reasonable, fixed-size chunks. This results in a 10x
        # improvement to bench_sendall.py, while having no measurable impact on
        # CPython (since it doesn't copy at all the only extra overhead is
        # a few python function calls, which is negligible for large inputs).

        # See https://bitbucket.org/pypy/pypy/issues/2091/non-blocking-socketsend-slow-gevent

        # Too small of a chunk (the socket's buf size is usually too
        # small) results in reduced perf due to *too many* calls to send and too many
        # small copies. With a buffer of 143K (the default on my system), for
        # example, bench_sendall.py yields ~264MB/s, while using 1MB yields
        # ~653MB/s (matching CPython). 1MB is arbitrary and might be better
        # chosen, say, to match a page size?
        chunk_size = max(self.getsockopt(SOL_SOCKET, SO_SNDBUF), 1024 * 1024)

        data_sent = 0
        end = None
        timeleft = None
        if self.timeout is not None:
            timeleft = self.timeout
            end = time.time() + timeleft

        while data_sent < len_data_memory:
            chunk_end = min(data_sent + chunk_size, len_data_memory)
            chunk = data_memory[data_sent:chunk_end]

            timeleft = self.__send_chunk(chunk, flags, timeleft, end)
            data_sent += len(chunk) # Guaranteed it sent the whole thing