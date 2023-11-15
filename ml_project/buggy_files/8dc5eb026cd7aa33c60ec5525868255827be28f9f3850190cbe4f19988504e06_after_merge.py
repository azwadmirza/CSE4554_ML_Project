    def _get_memory(data):
        try:
            mv = memoryview(data)
            if mv.shape:
                return mv
            # No shape, probably working with a ctypes object,
            # or something else exotic that supports the buffer interface
            return mv.tobytes()
        except TypeError:
            # fixes "python2.7 array.array doesn't support memoryview used in
            # gevent.socket.send" issue
            # (http://code.google.com/p/gevent/issues/detail?id=94)
            return buffer(data)