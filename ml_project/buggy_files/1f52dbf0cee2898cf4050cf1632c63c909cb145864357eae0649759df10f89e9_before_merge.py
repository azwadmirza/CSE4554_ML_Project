    def tile_fetch_tileable(self, tileable):
        """
        Find the owner of the input tensor and ask for tiling.
        """
        tileable_key = tileable.key
        graph_ref = self.ctx.actor_ref(self._session_ref.get_graph_ref_by_tleable_key(tileable_key))
        fetch_graph = deserialize_graph(graph_ref.build_fetch_graph(tileable_key))
        return list(fetch_graph)[0]