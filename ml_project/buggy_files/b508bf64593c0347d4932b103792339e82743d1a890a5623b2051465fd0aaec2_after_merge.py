    def _start_spinning(self):
        try:
            while not self._stop_running.is_set():
                self.fh.write(next(self.spinner_cycle) + ' ')
                self.fh.flush()
                sleep(0.10)
                self.fh.write('\b' * self._indicator_length)
        except EnvironmentError as e:
            if e.errno in (EPIPE, ESHUTDOWN):
                self.stop()
            else:
                raise