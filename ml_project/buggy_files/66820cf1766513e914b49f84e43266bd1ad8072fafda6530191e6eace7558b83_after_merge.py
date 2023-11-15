    def extract_descriptor(self):
        ret = NetworkDescriptor()
        topological_node_list = self.topological_order
        for u in topological_node_list:
            for v, layer_id in self.adj_list[u]:
                layer = self.layer_list[layer_id]
                if is_layer(layer, 'Conv') and layer.kernel_size not in [1, (1,), (1, 1), (1, 1, 1)]:
                    ret.add_conv_width(layer_width(layer))
                if is_layer(layer, 'Dense'):
                    ret.add_dense_width(layer_width(layer))

        # The position of each node, how many Conv and Dense layers before it.
        pos = [0] * len(topological_node_list)
        print(sorted(topological_node_list))
        for v in topological_node_list:
            layer_count = 0
            for u, layer_id in self.reverse_adj_list[v]:
                layer = self.layer_list[layer_id]
                weighted = 0
                if (is_layer(layer, 'Conv') and layer.kernel_size not in [1, (1,), (1, 1), (1, 1, 1)]) \
                        or is_layer(layer, 'Dense'):
                    weighted = 1
                layer_count = max(pos[u] + weighted, layer_count)
            pos[v] = layer_count

        for u in topological_node_list:
            for v, layer_id in self.adj_list[u]:
                if pos[u] == pos[v]:
                    continue
                layer = self.layer_list[layer_id]
                if is_layer(layer, 'Concatenate'):
                    ret.add_skip_connection(pos[u], pos[v], NetworkDescriptor.CONCAT_CONNECT)
                if is_layer(layer, 'Add'):
                    ret.add_skip_connection(pos[u], pos[v], NetworkDescriptor.ADD_CONNECT)

        return ret