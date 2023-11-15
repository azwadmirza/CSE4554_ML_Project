    def execute_graph(self, session_id, graph_key, graph_ser, io_meta, data_metas,
                      calc_device=None, send_addresses=None, callback=None):
        """
        Submit graph to the worker and control the execution
        :param session_id: session id
        :param graph_key: graph key
        :param graph_ser: serialized executable graph
        :param io_meta: io meta of the chunk
        :param data_metas: data meta of each input chunk, as a dict
        :param calc_device: device for calculation, can be 'gpu' or 'cpu'
        :param send_addresses: targets to send results after execution
        :param callback: promise callback
        """
        session_graph_key = (session_id, graph_key)
        callback = callback or []
        if not isinstance(callback, list):
            callback = [callback]
        try:
            all_callbacks = self._graph_records[session_graph_key].finish_callbacks or []
            self._graph_records[session_graph_key].finish_callbacks.extend(callback)
            if not self._graph_records[session_graph_key].retry_pending:
                self._graph_records[session_graph_key].finish_callbacks = all_callbacks + callback
                return
        except KeyError:
            all_callbacks = []
        all_callbacks.extend(callback)

        calc_device = calc_device or 'cpu'
        if calc_device == 'cpu':  # pragma: no cover
            if options.vineyard.socket:
                preferred_data_device = DataStorageDevice.VINEYARD
            else:
                preferred_data_device = DataStorageDevice.SHARED_MEMORY
        else:
            preferred_data_device = DataStorageDevice.CUDA

        # todo change this when handling multiple devices
        if preferred_data_device == DataStorageDevice.CUDA:
            slot = self._dispatch_ref.get_slots(calc_device)[0]
            proc_id = self.ctx.distributor.distribute(slot)
            preferred_data_device = (proc_id, preferred_data_device)

        graph_record = self._graph_records[(session_id, graph_key)] = GraphExecutionRecord(
            graph_ser, ExecutionState.ALLOCATING,
            io_meta=io_meta,
            data_metas=data_metas,
            chunk_targets=io_meta['chunks'],
            data_targets=list(io_meta.get('data_targets') or io_meta['chunks']),
            shared_input_chunks=set(io_meta.get('shared_input_chunks', [])),
            send_addresses=send_addresses,
            finish_callbacks=all_callbacks,
            calc_device=calc_device,
            preferred_data_device=preferred_data_device,
            no_prepare_chunk_keys=io_meta.get('no_prepare_chunk_keys') or set(),
        )

        _, long_op_string = concat_operand_keys(graph_record.graph, decompose=True)
        if long_op_string != graph_record.op_string:
            long_op_string = graph_record.op_string + ':' + long_op_string
        logger.debug('Worker graph %s(%s) targeting at %r accepted.', graph_key,
                     long_op_string, graph_record.chunk_targets)
        self._update_state(session_id, graph_key, ExecutionState.ALLOCATING)

        try:
            del self._result_cache[session_graph_key]
        except KeyError:
            pass

        @log_unhandled
        def _handle_success(*_):
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

            self._result_cache[(session_id, graph_key)] = GraphResultRecord(*exc, succeeded=False)
            self._invoke_finish_callbacks(session_id, graph_key)

        # collect target data already computed
        attrs = self.storage_client.get_data_attrs(session_id, graph_record.data_targets)
        save_attrs = dict((k, v) for k, v in zip(graph_record.data_targets, attrs) if v)

        # when all target data are computed, report success directly
        if all(k in save_attrs for k in graph_record.data_targets):
            logger.debug('All predecessors of graph %s already computed, call finish directly.', graph_key)
            sizes = dict((k, v.size) for k, v in save_attrs.items())
            shapes = dict((k, v.shape) for k, v in save_attrs.items())
            self._result_cache[(session_id, graph_key)] = GraphResultRecord(sizes, shapes)
            _handle_success()
        else:
            try:
                quota_request = self._prepare_quota_request(session_id, graph_key)
            except PinDataKeyFailed:
                logger.debug('Failed to pin chunk for graph %s', graph_key)

                # cannot pin input chunks: retry later
                retry_delay = graph_record.retry_delay + 0.5 + random.random()
                graph_record.retry_delay = min(1 + graph_record.retry_delay, 30)
                graph_record.retry_pending = True

                self.ref().execute_graph(
                    session_id, graph_key, graph_record.graph_serialized, graph_record.io_meta,
                    graph_record.data_metas, calc_device=calc_device, send_addresses=send_addresses,
                    _tell=True, _delay=retry_delay)
                return

            promise.finished() \
                .then(lambda *_: self._mem_quota_ref.request_batch_quota(
                    quota_request, _promise=True) if quota_request else None) \
                .then(lambda *_: self._prepare_graph_inputs(session_id, graph_key)) \
                .then(lambda *_: self._dispatch_ref.acquire_free_slot(calc_device, _promise=True)) \
                .then(lambda uid: self._send_calc_request(session_id, graph_key, uid)) \
                .then(lambda saved_keys: self._store_results(session_id, graph_key, saved_keys)) \
                .then(_handle_success, _handle_rejection)