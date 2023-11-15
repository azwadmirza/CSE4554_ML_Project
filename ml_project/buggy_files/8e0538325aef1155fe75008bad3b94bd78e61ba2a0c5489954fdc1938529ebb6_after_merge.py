    def execute_graph(self, session_id, graph_key, graph_ser, io_meta, data_sizes, send_targets=None,
                      callback=None):
        """
        Submit graph to the worker and control the execution
        :param session_id: session id
        :param graph_key: graph key
        :param graph_ser: serialized executable graph
        :param io_meta: io meta of the chunk
        :param data_sizes: data size of each input chunk, as a dict
        :param send_targets: targets to send results after execution
        :param callback: promise callback
        """
        from ..tensor.expressions.datasource import TensorFetchChunk
        data_sizes = data_sizes or dict()
        graph = deserialize_graph(graph_ser)
        targets = io_meta['chunks']
        chunks_use_once = set(io_meta.get('input_chunks', [])) - set(io_meta.get('shared_input_chunks', []))

        graph_ops = ','.join(type(c.op).__name__ for c in graph if not isinstance(c.op, TensorFetchChunk))
        logger.debug('Worker graph %s(%s) targeting at %r accepted.', graph_key, graph_ops, targets)

        self._update_stage_info(session_id, graph_key, graph_ops, 'allocate_resource')

        # add callbacks to callback store
        if callback is None:
            callback = []
        elif not isinstance(callback, list):
            callback = [callback]
        self._callbacks[graph_key].extend(callback)
        if graph_key in self._callback_cache:
            del self._callback_cache[graph_key]

        unspill_keys = []
        transfer_keys = []
        calc_keys = set()

        alloc_mem_batch = dict()
        alloc_cache_batch = dict()
        input_chunk_keys = dict()

        if self._status_ref:
            self.estimate_graph_finish_time(graph_key, graph)

        # collect potential allocation sizes
        for chunk in graph:
            if not isinstance(chunk.op, TensorFetchChunk) and chunk.key in targets:
                # use estimated size as potential allocation size
                calc_keys.add(chunk.key)
                alloc_mem_batch[chunk.key] = chunk.nbytes * 2
                alloc_cache_batch[chunk.key] = chunk.nbytes
            else:
                # use actual size as potential allocation size
                input_chunk_keys[chunk.key] = data_sizes.get(chunk.key, chunk.nbytes)

        calc_keys = list(calc_keys)

        keys_to_pin = list(input_chunk_keys.keys())
        try:
            self._pin_requests[graph_key] = set(self._chunk_holder_ref.pin_chunks(graph_key, keys_to_pin))
        except PinChunkFailed:
            # cannot pin input chunks: retry later
            callback = self._callbacks[graph_key]
            self._cleanup_graph(session_id, graph_key)

            retry_delay = self._retry_delays[graph_key] + 0.5 + random.random()
            self._retry_delays[graph_key] = min(1 + self._retry_delays[graph_key], 30)
            self.ref().execute_graph(session_id, graph_key, graph_ser, io_meta, data_sizes, send_targets, callback,
                                     _tell=True, _delay=retry_delay)
            return

        load_chunk_sizes = dict((k, v) for k, v in input_chunk_keys.items()
                                if k not in self._pin_requests[graph_key])
        alloc_mem_batch.update((self._build_load_key(graph_key, k), v)
                               for k, v in load_chunk_sizes.items() if k in chunks_use_once)
        self._chunk_holder_ref.spill_size(sum(alloc_cache_batch.values()), _tell=True)

        # build allocation promises
        batch_alloc_promises = []
        if alloc_mem_batch:
            self._mem_requests[graph_key] = list(alloc_mem_batch.keys())
            batch_alloc_promises.append(self._mem_quota_ref.request_batch_quota(alloc_mem_batch, _promise=True))

        @log_unhandled
        def _prepare_inputs(*_):
            if graph_key in self._stop_requests:
                raise ExecutionInterrupted

            logger.debug('Start preparing input data for graph %s', graph_key)
            self._update_stage_info(session_id, graph_key, graph_ops, 'prepare_inputs')
            prepare_promises = []

            handled_keys = set()
            for chunk in graph:
                if chunk.key in handled_keys:
                    continue
                if not isinstance(chunk.op, TensorFetchChunk):
                    continue
                handled_keys.add(chunk.key)

                if self._chunk_holder_ref.is_stored(chunk.key):
                    # data already in plasma: we just pin it
                    pinned_keys = self._chunk_holder_ref.pin_chunks(graph_key, chunk.key)
                    if chunk.key in pinned_keys:
                        self._mem_quota_ref.release_quota(self._build_load_key(graph_key, chunk.key))
                        continue

                if spill_exists(chunk.key):
                    if chunk.key in chunks_use_once:
                        # input only use in current operand, we only need to load it into process memory
                        continue
                    self._mem_quota_ref.release_quota(self._build_load_key(graph_key, chunk.key))
                    load_fun = partial(lambda gk, ck, *_: self._chunk_holder_ref.pin_chunks(gk, ck),
                                       graph_key, chunk.key)
                    unspill_keys.append(chunk.key)
                    prepare_promises.append(ensure_chunk(self, session_id, chunk.key, move_to_end=True) \
                                            .then(load_fun))
                    continue

                # load data from another worker
                chunk_meta = self.get_meta_ref(session_id, chunk.key) \
                    .get_chunk_meta(session_id, chunk.key)
                if chunk_meta is None:
                    raise DependencyMissing('Dependency %s not met on sending.' % chunk.key)

                worker_priorities = []
                for w in chunk_meta.workers:
                    # todo sort workers by speed of network and other possible factors
                    worker_priorities.append((w, (0, )))

                transfer_keys.append(chunk.key)

                # fetch data from other workers, if one fails, try another
                sorted_workers = sorted(worker_priorities, key=lambda pr: pr[1])
                p = self._fetch_remote_data(session_id, graph_key, chunk.key, sorted_workers[0][0],
                                            ensure_cached=chunk.key not in chunks_use_once)
                for wp in sorted_workers[1:]:
                    p = p.catch(functools.partial(self._fetch_remote_data, session_id, graph_key, chunk.key, wp[0],
                                                  ensure_cached=chunk.key not in chunks_use_once))
                prepare_promises.append(p)

            logger.debug('Graph key %s: Targets %r, unspill keys %r, transfer keys %r',
                         graph_key, targets, unspill_keys, transfer_keys)
            return promise.all_(prepare_promises)

        @log_unhandled
        def _wait_free_slot(*_):
            logger.debug('Waiting for free CPU slot for graph %s', graph_key)
            self._update_stage_info(session_id, graph_key, graph_ops, 'fetch_free_slot')
            return self._dispatch_ref.get_free_slot('cpu', _promise=True)

        @log_unhandled
        def _send_calc_request(calc_uid):
            if graph_key in self._stop_requests:
                raise ExecutionInterrupted

            # get allocation for calc, in case that memory exhausts
            target_allocs = dict()
            for chunk in graph:
                if isinstance(chunk.op, TensorFetchChunk):
                    if not self._chunk_holder_ref.is_stored(chunk.key):
                        alloc_key = self._build_load_key(graph_key, chunk.key)
                        if alloc_key in alloc_mem_batch:
                            target_allocs[alloc_key] = alloc_mem_batch[alloc_key]
                elif chunk.key in targets:
                    target_allocs[chunk.key] = alloc_mem_batch[chunk.key]

            logger.debug('Start calculation for graph %s', graph_key)

            self._update_stage_info(session_id, graph_key, graph_ops, 'calculate')
            calc_ref = self.promise_ref(calc_uid)

            self.estimate_graph_finish_time(graph_key, graph, calc_fetch=False)
            # make sure that memory suffices before actually run execution
            return self._mem_quota_ref.request_batch_quota(target_allocs, _promise=True) \
                .then(lambda *_: self._deallocate_scheduler_resource(session_id, graph_key, delay=2)) \
                .then(lambda *_: calc_ref.calc(session_id, graph_ser, targets, _promise=True))

        @log_unhandled
        def _dump_cache(inproc_uid, save_sizes):
            # do some clean up
            self._deallocate_scheduler_resource(session_id, graph_key)
            inproc_ref = self.promise_ref(inproc_uid)

            if graph_key in self._stop_requests:
                inproc_ref.remove_cache(calc_keys, _tell=True)
                raise ExecutionInterrupted

            self._update_stage_info(session_id, graph_key, graph_ops, 'dump_cache')

            logger.debug('Graph %s: Start putting %r into shared cache. Target actor uid %s.',
                         graph_key, calc_keys, inproc_uid)

            self._chunk_holder_ref.unpin_chunks(graph_key, list(set(c.key for c in graph)), _tell=True)
            if logger.getEffectiveLevel() <= logging.DEBUG:
                self._dump_execution_stages()
                # self._cache_ref.dump_cache_status(_tell=True)

            self._size_cache[graph_key] = save_sizes

            if not send_targets:
                # no endpoints to send, dump keys into shared memory and return
                logger.debug('Worker graph %s(%s) finished execution. Dumping %r into plasma...',
                             graph_key, graph_ops, calc_keys)
                return inproc_ref.dump_cache(calc_keys, _promise=True)
            else:
                # dump keys into shared memory and send
                logger.debug('Worker graph %s(%s) finished execution. Dumping %r into plasma '
                             'while actively transferring %r...',
                             graph_key, graph_ops, calc_keys, send_targets)

                return inproc_ref.dump_cache(calc_keys, _promise=True) \
                        .then(_do_active_transfer)

        @log_unhandled
        def _do_active_transfer(*_):
            # transfer the result chunk to expected endpoints
            @log_unhandled
            def _send_chunk(sender_uid, chunk_key, target_addrs):
                sender_ref = self.promise_ref(sender_uid)
                logger.debug('Request for chunk %s sent to %s', chunk_key, target_addrs)
                return sender_ref.send_data(session_id, chunk_key, target_addrs, ensure_cached=False,
                                            timeout=options.worker.prepare_data_timeout, _promise=True)

            if graph_key in self._mem_requests:
                self._mem_quota_ref.release_quotas(self._mem_requests[graph_key], _tell=True)
                del self._mem_requests[graph_key]

            promises = []
            for key, targets in send_targets.items():
                promises.append(self._dispatch_ref.get_free_slot('sender', _promise=True) \
                                .then(partial(_send_chunk, chunk_key=key, target_addrs=targets)) \
                                .catch(lambda *_: None))
            return promise.all_(promises)

        @log_unhandled
        def _handle_rejection(*exc):
            # some error occurred...
            logger.debug('Entering _handle_rejection() for graph %s', graph_key)
            if logger.getEffectiveLevel() <= logging.DEBUG:
                self._dump_execution_stages()
                # self._cache_ref.dump_cache_status(_tell=True)

            if graph_key in self._stop_requests:
                self._stop_requests.remove(graph_key)

            self._mem_quota_ref.cancel_requests(list(alloc_mem_batch.keys()), _tell=True)

            if not issubclass(exc[0], _WORKER_RETRY_ERRORS):
                # exception not retryable: call back to scheduler
                if isinstance(exc[0], ExecutionInterrupted):
                    logger.warning('Execution of graph %s interrupted.', graph_key)
                else:
                    try:
                        six.reraise(*exc)
                    except:
                        logger.exception('Unexpected error occurred in executing %s', graph_key)
                self._invoke_finish_callbacks(session_id, graph_key, *exc, **dict(_accept=False))
                return

            logger.debug('Graph %s rejected from execution because of %s', graph_key, exc[0].__name__)

            cb = self._callbacks[graph_key]
            self._cleanup_graph(session_id, graph_key)

            if issubclass(exc[0], ObjectNotInPlasma):
                retry_delay = 0
            else:
                retry_delay = self._retry_delays[graph_key] + 0.5 + random.random()
                self._retry_delays[graph_key] = min(1 + self._retry_delays[graph_key], 30)

            self.ref().execute_graph(session_id, graph_key, graph_ser, io_meta, data_sizes, send_targets, cb,
                                     _tell=True, _delay=retry_delay)

        promise.all_(batch_alloc_promises).then(_prepare_inputs) \
            .then(_wait_free_slot).then(_send_calc_request) \
            .then(_dump_cache).then(lambda *_: self._invoke_finish_callbacks(session_id, graph_key,
                                                                             self._size_cache.get(graph_key))) \
            .catch(_handle_rejection)