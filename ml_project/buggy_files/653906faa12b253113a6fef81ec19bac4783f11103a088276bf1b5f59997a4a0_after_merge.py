        def _cache_result(result_sizes):
            save_sizes.update(result_sizes)
            self._result_cache[(session_id, graph_key)] = GraphResultRecord(save_sizes)