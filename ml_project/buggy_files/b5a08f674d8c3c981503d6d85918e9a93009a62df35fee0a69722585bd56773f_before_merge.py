    def start_execution(self, session_id, graph_key, send_addresses=None, callback=None):
        """
        Submit graph to the worker and control the execution
        :param session_id: session id
        :param graph_key: key of the execution graph
        :param send_addresses: targets to send results after execution
        :param callback: promise callback
        """
        graph_record = self._graph_records[(session_id, graph_key)]
        if send_addresses:
            graph_record.send_addresses = send_addresses

        # add callbacks to callback store
        if callback is None:
            callback = []
        elif not isinstance(callback, list):
            callback = [callback]
        graph_record.finish_callbacks.extend(callback)
        try:
            del self._result_cache[(session_id, graph_key)]
        except KeyError:
            pass

        @log_unhandled
        def _wait_free_slot(*_):
            return self._dispatch_ref.get_free_slot('cpu', _promise=True)

        @log_unhandled
        def _handle_success(*_):
            self._notify_successors(session_id, graph_key)
            self._invoke_finish_callbacks(session_id, graph_key)

        @log_unhandled
        def _handle_rejection(*exc):
            # some error occurred...
            logger.debug('Entering _handle_rejection() for graph %s', graph_key)
            self._dump_execution_states()

            if graph_record.stop_requested:
                graph_record.stop_requested = False
                if not isinstance(exc[1], ExecutionInterrupted):
                    exc = build_exc_info(ExecutionInterrupted)

            if isinstance(exc[1], ExecutionInterrupted):
                logger.warning('Execution of graph %s interrupted.', graph_key)
            else:
                logger.exception('Unexpected error occurred in executing graph %s', graph_key, exc_info=exc)

            self._result_cache[(session_id, graph_key)] = GraphResultRecord(*exc, **dict(succeeded=False))
            self._invoke_finish_callbacks(session_id, graph_key)

        # collect target data already computed
        save_sizes = dict()
        for target_key in graph_record.data_targets:
            if self._chunk_store.contains(session_id, target_key):
                save_sizes[target_key] = self._chunk_store.get_actual_size(session_id, target_key)
            elif spill_exists(target_key):
                save_sizes[target_key] = get_spill_data_size(target_key)

        # when all target data are computed, report success directly
        if all(k in save_sizes for k in graph_record.data_targets):
            logger.debug('All predecessors of graph %s already computed, call finish directly.', graph_key)
            self._result_cache[(session_id, graph_key)] = GraphResultRecord(save_sizes)
            _handle_success()
        else:
            promise.finished() \
                .then(lambda: self._prepare_graph_inputs(session_id, graph_key)) \
                .then(_wait_free_slot) \
                .then(lambda uid: self._send_calc_request(session_id, graph_key, uid)) \
                .then(lambda uid, sizes: self._dump_cache(session_id, graph_key, uid, sizes)) \
                .then(_handle_success, _handle_rejection)