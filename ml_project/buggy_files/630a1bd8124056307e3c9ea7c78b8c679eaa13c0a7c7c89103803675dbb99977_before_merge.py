    def build_fetch_graph(self, tileable_key):
        """
        Convert single tensor to tiled fetch tensor and put into a graph which only contains one tensor
        :param tileable_key: the key of tensor
        """
        tileable = self._get_tileable_by_key(tileable_key)
        graph = DAG()

        new_tileable = build_fetch_tileable(tileable)
        graph.add_node(new_tileable)
        return serialize_graph(graph)