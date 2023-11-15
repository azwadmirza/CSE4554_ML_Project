    def stop_process_thread(self):
        _log.debug("Stopping the process thread.")
        if self._process_thread is None:
            return

        # Tell the loop it needs to die.
        self._stop_process_loop = True
        # Wake the loop.
        self._event_queue.put(None)

        # 9 seconds as configuration timeout is 10 seconds.
        self._process_thread.join(9.0)
        if self._process_thread.is_alive():
            _log.error("Failed to stop process thread during reconfiguration!")

        self._process_thread = None
        _log.debug("Process thread stopped.")