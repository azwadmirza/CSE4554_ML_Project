    def calc(self, session_id, graph_key, ser_graph, chunk_targets, callback):
        """
        Do actual calculation. This method should be called when all data
        is available (i.e., either in shared cache or in memory)
        :param session_id: session id
        :param graph_key: key of executable graph
        :param ser_graph: serialized executable graph
        :param chunk_targets: keys of target chunks
        :param callback: promise callback, returns the uid of InProcessCacheActor
        """
        self._executing_set.add(graph_key)
        graph = deserialize_graph(ser_graph)
        chunk_targets = set(chunk_targets)
        keys_to_fetch = self._get_keys_to_fetch(graph)

        self._make_quotas_local(session_id, graph_key, keys_to_fetch + list(chunk_targets),
                                process_quota=True)

        def _start_calc(context_dict):
            return self._calc_results(session_id, graph_key, graph, context_dict, chunk_targets)

        def _finalize(keys, exc_info):
            if not self._marked_as_destroy:
                self._dispatch_ref.register_free_slot(self.uid, self._slot_name, _tell=True, _wait=False)

            if not exc_info:
                self.tell_promise(callback, keys)
            else:
                try:
                    self.tell_promise(callback, *exc_info, _accept=False)
                except:
                    self.tell_promise(callback, *build_exc_info(
                        SystemError, f'Failed to send errors to scheduler, type: {exc_info[0].__name__}, '
                                     f'message: {str(exc_info[1])}'), _accept=False)
                    raise

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

        return self._fetch_keys_to_process(session_id, keys_to_fetch) \
            .then(lambda context_dict: _start_calc(context_dict)) \
            .then(lambda keys: _finalize(keys, None), lambda *exc_info: _finalize(None, exc_info))