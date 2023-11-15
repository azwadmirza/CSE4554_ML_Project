    def _prepare_graph_inputs(self, session_id, graph_key):
        """
        Load input data from spilled storage and other workers
        :param session_id: session id
        :param graph_key: key of the execution graph
        """
        graph_record = self._graph_records[(session_id, graph_key)]
        if graph_record.stop_requested:
            raise ExecutionInterrupted

        unspill_keys = []
        transfer_keys = []

        logger.debug('Start preparing input data for graph %s', graph_key)
        self._update_state(session_id, graph_key, ExecutionState.PREPARING_INPUTS)
        prepare_promises = []
        chunks_use_once = graph_record.chunks_use_once

        handled_keys = set()
        for chunk in graph_record.graph:
            if not isinstance(chunk.op, TensorFetch):
                continue
            if chunk.key in handled_keys:
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
            worker_results = chunk_meta.workers

            worker_priorities = []
            for worker_ip in worker_results:
                # todo sort workers by speed of network and other possible factors
                worker_priorities.append((worker_ip, (0, )))

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
                     graph_key, graph_record.targets, unspill_keys, transfer_keys)
        return promise.all_(prepare_promises)