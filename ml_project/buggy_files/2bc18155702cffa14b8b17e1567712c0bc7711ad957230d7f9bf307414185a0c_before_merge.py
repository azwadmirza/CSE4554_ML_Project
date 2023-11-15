    def lock(self, session_id, data_keys, callback):
        logger.debug('Requesting lock for %r on %s', data_keys, self.uid)
        self._work_items.append((None, session_id, data_keys, None, True, callback))
        if self._lock_free or not self._cur_work_items:
            self._submit_next()