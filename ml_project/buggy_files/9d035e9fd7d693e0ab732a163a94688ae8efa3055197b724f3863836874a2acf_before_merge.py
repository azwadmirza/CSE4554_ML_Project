    def build_fetch_graph(self, tensor_key):
        """
        Convert single tensor to tiled fetch tensor and put into a graph which only contains one tensor
        :param tensor_key: the key of tensor
        """
        tiled_tensor = self._get_tensor_by_key(tensor_key)
        graph = DAG()

        chunks = []
        for c in tiled_tensor.chunks:
            fetch_op = TensorFetch(dtype=c.dtype)
            fetch_chunk = fetch_op.new_chunk(None, c.shape, c.index, _key=c.key)
            chunks.append(fetch_chunk)

        new_op = TensorFetch(dtype=tiled_tensor.dtype)
        new_tensor = new_op.new_tensor(None, tiled_tensor.shape, chunks=chunks,
                                       nsplits=tiled_tensor.nsplits, _key=tiled_tensor.key)
        graph.add_node(new_tensor)
        return serialize_graph(graph)