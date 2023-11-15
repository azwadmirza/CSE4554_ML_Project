    def _estimate_calc_memory(self, session_id, graph_key):
        graph_record = self._graph_records[(session_id, graph_key)]
        size_ctx = dict((k, (v.chunk_size, v.chunk_size))
                        for k, v in graph_record.data_metas.items())
        executor = Executor(storage=size_ctx, sync_provider_type=Executor.SyncProviderType.MOCK)
        res = executor.execute_graph(graph_record.graph, graph_record.chunk_targets, mock=True)

        targets = graph_record.chunk_targets
        target_sizes = dict(zip(targets, res))

        total_mem = sum(target_sizes[key][1] for key in targets)
        if total_mem:
            for key in targets:
                r = target_sizes[key]
                target_sizes[key] = (r[0], max(r[1], r[1] * executor.mock_max_memory // total_mem))
        return target_sizes