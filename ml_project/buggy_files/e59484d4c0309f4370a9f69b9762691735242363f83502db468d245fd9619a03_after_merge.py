    def start_process_thread(self):
        if self._process_loop_in_greenlet:
            self._process_thread = self.core.spawn(self._process_loop)
            self._process_thread.start()
            _log.debug("Process greenlet started.")
        else:
            self._process_thread = Thread(target=self._process_loop)
            self._process_thread.daemon = True  # Don't wait on thread to exit.
            self._process_thread.start()
            _log.debug("Process thread started.")