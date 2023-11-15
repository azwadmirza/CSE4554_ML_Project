    def sendall(self, data, flags=0):
        # XXX When we run on PyPy3, see the notes in _socket2.py's sendall()
        data_memory = _get_memory(data)
        len_data_memory = len(data_memory)
        if not len_data_memory:
            # Don't try to send empty data at all, no point, and breaks ssl
            # See issue 719
            return 0

        if self.timeout is None:
            data_sent = 0
            while data_sent < len_data_memory:
                data_sent += self.send(data_memory[data_sent:], flags)
        else:
            timeleft = self.timeout
            end = time.time() + timeleft
            data_sent = 0
            while True:
                data_sent += self.send(data_memory[data_sent:], flags, timeout=timeleft)
                if data_sent >= len_data_memory:
                    break
                timeleft = end - time.time()
                if timeleft <= 0:
                    raise timeout('timed out')