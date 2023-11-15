        def _finalize(keys, exc_info):
            if not self._marked_as_destroy:
                self._dispatch_ref.register_free_slot(self.uid, self._slot_name, _tell=True, _wait=False)

            if not exc_info:
                self.tell_promise(callback, keys)
            else:
                self.tell_promise(callback, *exc_info, _accept=False)

            keys_to_release = [k for k in keys_to_fetch if get_chunk_key(k) not in chunk_targets]
            if exc_info:
                keys_to_release.extend(chunk_targets)

            if self._remove_intermediate:
                keys_to_delete = keys_to_release
            else:
                keys_to_delete = []

            if keys_to_delete:
                self.storage_client.delete(session_id, keys_to_delete, [self._calc_intermediate_device])
            logger.debug('Finish calculating operand %s.', graph_key)