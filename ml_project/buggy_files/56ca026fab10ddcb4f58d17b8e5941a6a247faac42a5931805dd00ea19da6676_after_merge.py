    def sendall(self, data, flags=0):
        data_memory = _get_memory(data)
        if self.timeout is None:
            data_sent = 0
            while data_sent < len(data_memory):
                data_sent += self.send(data_memory[data_sent:], flags)
        else:
            timeleft = self.timeout
            end = time.time() + timeleft
            data_sent = 0
            while True:
                data_sent += self.send(data_memory[data_sent:], flags, timeout=timeleft)
                if data_sent >= len(data_memory):
                    break
                timeleft = end - time.time()
                if timeleft <= 0:
                    raise timeout('timed out')