    def _update_tileable_and_its_chunk_shapes(self):
        need_update_tileable_to_tiled = dict()
        for tileable in self._chunk_graph_builder.prev_tileable_graph:
            if tileable.key in self._target_tileable_finished:
                tiled = self._tileable_key_opid_to_tiled[tileable.key, tileable.op.id][-1]
                if not has_unknown_shape(tiled):
                    continue
                need_update_tileable_to_tiled[tileable] = tiled

        if len(need_update_tileable_to_tiled) == 0:
            return

        need_update_chunks = list(c for t in need_update_tileable_to_tiled.values() for c in t.chunks)
        chunk_metas = self.chunk_meta.batch_get_chunk_meta(
            self._session_id, list(c.key for c in need_update_chunks))
        for chunk, chunk_meta in zip(need_update_chunks, chunk_metas):
            chunk.data._shape = chunk_meta.chunk_shape

        for tileable, tiled in need_update_tileable_to_tiled.items():
            chunk_idx_to_shape = OrderedDict((c.index, c.shape) for c in tiled.chunks)
            nsplits = calc_nsplits(chunk_idx_to_shape)
            tiled._nsplits = nsplits
            if any(np.isnan(s) for s in tileable.shape):
                shape = tuple(sum(ns) for ns in nsplits)
                tileable._update_shape(shape)
                tiled._update_shape(shape)