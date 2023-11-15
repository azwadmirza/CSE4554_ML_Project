    def rx_thread(self):
        while self.running.is_set():
            msg = self.bus.recv(self.timeout)
            if msg is not None:
                for callback in self.listeners:
                    callback(msg)