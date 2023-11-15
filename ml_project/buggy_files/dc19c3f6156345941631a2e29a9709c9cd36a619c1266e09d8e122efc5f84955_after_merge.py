    def build_fetch_graph(self, tileable_key):
        """
        Convert single tileable node to tiled fetch tileable node and
        put into a graph which only contains one tileable node
        :param tileable_key: the key of tileable node
        """
        tileable = self._get_tileable_by_key(tileable_key)
        graph = DAG()

        new_tileable = build_fetch_tileable(tileable).data
        graph.add_node(new_tileable)
        return serialize_graph(graph)