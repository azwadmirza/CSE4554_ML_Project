    def stop(self):
        self.running.clear()
        if self.timeout is not None:
            self._reader.join(self.timeout + 0.1)