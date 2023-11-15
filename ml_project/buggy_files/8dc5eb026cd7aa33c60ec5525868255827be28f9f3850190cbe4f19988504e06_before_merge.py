    def _get_memory(string, offset):
        try:
            return memoryview(string)[offset:]
        except TypeError:
            # fixes "python2.7 array.array doesn't support memoryview used in
            # gevent.socket.send" issue
            # (http://code.google.com/p/gevent/issues/detail?id=94)
            return buffer(string, offset)