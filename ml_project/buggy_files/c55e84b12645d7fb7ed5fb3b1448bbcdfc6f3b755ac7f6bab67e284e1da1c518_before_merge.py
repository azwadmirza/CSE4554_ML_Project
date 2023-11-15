    def run(self):
        state = None
        while True:
            state = self._worker(old_state=state)
            if state == State.RELOAD_CONF:
                self.freqtrade = self._reconfigure()