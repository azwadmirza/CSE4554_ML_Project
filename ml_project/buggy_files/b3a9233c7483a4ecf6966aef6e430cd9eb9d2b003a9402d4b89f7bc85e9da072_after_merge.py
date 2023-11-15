    def load_from(self, dest_device, session_id, data_keys, src_device, callback):
        logger.debug('Copying %r from %s into %s submitted in %s',
                     data_keys, src_device, dest_device, self.uid)
        self._work_items.append((dest_device, session_id, data_keys, src_device, False, callback))
        if len(self._cur_work_items) < self._io_parallel_num:
            self._submit_next()