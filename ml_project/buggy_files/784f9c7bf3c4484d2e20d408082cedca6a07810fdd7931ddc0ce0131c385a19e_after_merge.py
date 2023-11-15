    def _maybe_garbage_collect(self):
        if time.time() < self._next_gc:
            return
        self._logger.info("Garbage collecting store")
        self._scheduler_session.garbage_collect_store(self._target_size_bytes)
        self._logger.info("Done garbage collecting store")
        self._set_next_gc()