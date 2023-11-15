    def _prepare_graph_inputs(self, session_id, graph_key):
        """
        Load input data from spilled storage and other workers
        :param session_id: session id
        :param graph_key: key of the execution graph
        """
        storage_client = self.storage_client
        graph_record = self._graph_records[(session_id, graph_key)]
        graph = graph_record.graph
        input_metas = graph_record.io_meta.get('input_data_metas', dict())

        if graph_record.stop_requested:
            raise ExecutionInterrupted

        logger.debug('Start preparing input data for graph %s', graph_key)
        self._update_state(session_id, graph_key, ExecutionState.PREPARING_INPUTS)
        prepare_promises = []

        input_keys = set()
        shuffle_keys = set()
        for chunk in graph:
            op = chunk.op
            if isinstance(op, Fetch):
                if chunk.key in graph_record.no_prepare_chunk_keys \
                        or chunk.key in graph_record.pure_dep_chunk_keys:
                    continue
                input_keys.add(op.to_fetch_key or chunk.key)
            elif isinstance(op, FetchShuffle):
                shuffle_key = get_chunk_shuffle_key(graph.successors(chunk)[0])
                for input_key in op.to_fetch_keys:
                    part_key = (input_key, shuffle_key)
                    input_keys.add(part_key)
                    shuffle_keys.add(part_key)

        local_keys = graph_record.pinned_keys & set(input_keys)
        non_local_keys = [k for k in input_keys if k not in local_keys]
        non_local_locations = storage_client.get_data_locations(session_id, non_local_keys)
        copy_keys = set(k for k, loc in zip(non_local_keys, non_local_locations) if loc)
        remote_keys = [k for k in non_local_keys if k not in copy_keys]

        # handle local keys
        self._release_shared_store_quotas(session_id, graph_key, local_keys)
        # handle move keys
        prepare_promises.extend(
            self._prepare_copy_keys(session_id, graph_key, copy_keys))
        # handle remote keys
        prepare_promises.extend(
            self._prepare_remote_keys(session_id, graph_key, remote_keys, input_metas))

        logger.debug('Graph key %s: Targets %r, loaded keys %r, copy keys %s, remote keys %r',
                     graph_key, graph_record.chunk_targets, local_keys, copy_keys, remote_keys)
        p = promise.all_(prepare_promises) \
            .then(lambda *_: logger.debug('Data preparation for graph %s finished', graph_key))
        return p