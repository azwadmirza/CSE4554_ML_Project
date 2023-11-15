    def execute_tileables(self, tileables, fetch=True, n_parallel=None, n_thread=None,
                          print_progress=False, mock=False, compose=True):
        graph = DirectedGraph()

        result_keys = []
        to_release_keys = []
        concat_keys = []
        for tileable in tileables:
            tileable.tiles()
            chunk_keys = [c.key for c in tileable.chunks]
            result_keys.extend(chunk_keys)

            if tileable.key in self.stored_tileables:
                self.stored_tileables[tileable.key][0].add(tileable.id)
            else:
                self.stored_tileables[tileable.key] = tuple([{tileable.id}, set(chunk_keys)])
            if not fetch:
                # no need to generate concat keys
                pass
            elif len(tileable.chunks) > 1:
                # if need to fetch data and chunks more than 1, we concatenate them into 1
                tileable = concat_tileable_chunks(tileable)
                chunk = tileable.chunks[0]
                result_keys.append(chunk.key)
                # the concatenated key
                concat_keys.append(chunk.key)
                # after return the data to user, we release the reference
                to_release_keys.append(chunk.key)
            else:
                concat_keys.append(tileable.chunks[0].key)

            # Do not do compose here, because building graph has not finished yet
            tileable.build_graph(graph=graph, tiled=True, compose=False,
                                 executed_keys=list(self._chunk_result.keys()))
        if compose:
            # finally do compose according to option
            graph.compose(keys=list(itertools.chain(*[[c.key for c in t.chunks]
                                                      for t in tileables])))

        self.execute_graph(graph, result_keys, n_parallel=n_parallel or n_thread,
                           print_progress=print_progress, mock=mock)

        results = self._chunk_result
        try:
            if fetch:
                return [results[k] for k in concat_keys]
            else:
                return
        finally:
            for k in to_release_keys:
                del results[k]