    def execute_tileable(self, tileable, n_parallel=None, n_thread=None, concat=False,
                         print_progress=False, mock=False, compose=True):
        if concat:
            # only for tests
            tileable.tiles()
            if len(tileable.chunks) > 1:
                tileable = tileable.op.concat_tileable_chunks(tileable)

        # shallow copy
        chunk_result = self._chunk_result.copy()
        graph = tileable.build_graph(cls=DirectedGraph, tiled=True, compose=compose)
        ret = self.execute_graph(graph, [c.key for c in tileable.chunks],
                                 n_parallel=n_parallel or n_thread,
                                 print_progress=print_progress, mock=mock,
                                 chunk_result=chunk_result)
        self._chunk_result.update(chunk_result)
        return ret