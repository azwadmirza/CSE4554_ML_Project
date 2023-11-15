    def start(self):
        self._shutdown = False

        # Spawn the worker threads.
        self._main_thread = eventlet.spawn(self.run)
        self._cleanup_thread = eventlet.spawn(self.cleanup)

        # Link the threads to the shutdown function. If either of the threads exited with error,
        # then initiate shutdown which will allow the waits below to throw exception to the
        # main process.
        self._main_thread.link(self.shutdown)
        self._cleanup_thread.link(self.shutdown)