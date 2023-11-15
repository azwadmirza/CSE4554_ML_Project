    def lock(self, session_id, data_keys, callback):
        logger.debug('Requesting lock for %r on %s', data_keys, self.uid)
        self._work_items.append((None, session_id, data_keys, None, True, callback))
        if len(self._cur_work_items) < self._io_parallel_num:
            self._submit_next()