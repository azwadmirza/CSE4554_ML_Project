    def _run(self):
        while not self._connection.done:
            queue = []
            with self._lock:
                # wait for available data
                while not self._queue and not self._connection.done:
                    self._waiting = True
                    self._cond_data_available.wait(1.0)
                    self._waiting = False
                    if self._queue:
                        self._cond_queue_swapped.notify()
                # take all data from queue for processing outside of the lock
                if self._queue:
                    queue = self._queue
                    self._queue = []
            # relay all data
            for data in queue:
                try:
                    self._connection.write_data(data)
                except Exception as e:
                    with self._cond:
                        self._error = e