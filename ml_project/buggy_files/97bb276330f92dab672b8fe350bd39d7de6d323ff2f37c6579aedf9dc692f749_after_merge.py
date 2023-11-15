    def _prepare_quota_request(self, session_id, graph_key):
        """
        Calculate quota request for an execution graph
        :param session_id: session id
        :param graph_key: key of the execution graph
        :return: allocation dict
        """
        try:
            graph_record = self._graph_records[(session_id, graph_key)]
        except KeyError:
            return None

        graph = graph_record.graph
        storage_client = self.storage_client
        input_data_sizes = dict((k, v.chunk_size) for k, v in graph_record.data_metas.items())
        alloc_mem_batch = dict()
        alloc_cache_batch = dict()
        input_chunk_keys = dict()

        if self._status_ref:
            self.estimate_graph_finish_time(session_id, graph_key)

        if graph_record.preferred_data_device == DataStorageDevice.SHARED_MEMORY or \
                graph_record.preferred_data_device == DataStorageDevice.VINEYARD:  # pragma: no cover
            memory_estimations = self._estimate_calc_memory(session_id, graph_key)
        else:
            memory_estimations = dict()

        graph_record.mem_overhead_keys = set()
        # collect potential allocation sizes
        for chunk in graph:
            op = chunk.op
            overhead_keys_and_shapes = []

            if isinstance(op, Fetch):
                if chunk.key in graph_record.no_prepare_chunk_keys \
                        or chunk.key in graph_record.pure_dep_chunk_keys:
                    continue
                # use actual size as potential allocation size
                input_chunk_keys[chunk.key] = input_data_sizes.get(chunk.key) or calc_data_size(chunk)
                overhead_keys_and_shapes = [(chunk.key, getattr(chunk, 'shape', None))]
            elif isinstance(op, FetchShuffle):
                shuffle_key = get_chunk_shuffle_key(graph.successors(chunk)[0])
                overhead_keys_and_shapes = chunk.extra_params.get('_shapes', dict()).items()
                for k in op.to_fetch_keys:
                    part_key = (k, shuffle_key)
                    try:
                        input_chunk_keys[part_key] = input_data_sizes[part_key]
                    except KeyError:
                        pass
            elif chunk.key in graph_record.chunk_targets:
                # use estimated size as potential allocation size
                estimation_data = memory_estimations.get(chunk.key)
                if not estimation_data:
                    continue
                quota_key = build_quota_key(session_id, chunk.key, owner=graph_key)
                cache_batch, alloc_mem_batch[quota_key] = estimation_data
                if not isinstance(chunk.key, tuple):
                    alloc_cache_batch[chunk.key] = cache_batch

            for key, shape in overhead_keys_and_shapes:
                overhead = calc_object_overhead(chunk, shape)
                if overhead:
                    graph_record.mem_overhead_keys.add(key)
                    quota_key = build_quota_key(session_id, key, owner=graph_key)
                    alloc_mem_batch[quota_key] = overhead

        keys_to_pin = list(input_chunk_keys.keys())
        graph_record.pinned_keys = set()
        self._pin_shared_data_keys(session_id, graph_key, keys_to_pin)

        for k, v in input_chunk_keys.items():
            quota_key = build_quota_key(session_id, k, owner=graph_key)
            if quota_key not in alloc_mem_batch:
                if k in graph_record.pinned_keys or k in graph_record.shared_input_chunks:
                    continue
            alloc_mem_batch[quota_key] = alloc_mem_batch.get(quota_key, 0) + v

        if alloc_cache_batch:
            storage_client.spill_size(sum(alloc_cache_batch.values()), [graph_record.preferred_data_device])

        graph_record.mem_request = alloc_mem_batch or dict()
        return alloc_mem_batch