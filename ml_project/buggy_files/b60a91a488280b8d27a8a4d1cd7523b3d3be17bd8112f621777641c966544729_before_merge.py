    def _merge_batch_norm(graph, nodes, pattern_id=1):
        expected_num_nodes = 4
        if pattern_id == 2:
            expected_num_nodes = 6
        elif pattern_id == 3:
            expected_num_nodes = 8
        assert len(nodes) == expected_num_nodes

        current_node = graph[nodes[1].inputs[0]]
        out_node = nodes[-1]
        bn_outputs = out_node.outputs[:]

        fused_bn_node = ParsedNode()
        fused_bn_node.op = 'BatchNorm'
        fused_bn_node.name = out_node.name + '_batch_norm'

        fused_bn_node.attr = {
            'gamma': np.squeeze(nodes[0].value.val),
            'beta': np.squeeze(nodes[2].value.val),
        }
        if pattern_id == 2:
            fused_bn_node.attr = {
                'mean': np.squeeze(nodes[0].value.val),
                'gamma': np.squeeze(nodes[2].value.val),
                'beta': np.squeeze(nodes[4].value.val),
            }
        elif pattern_id == 3:
            fused_bn_node.attr = {
                'mean': np.squeeze(nodes[0].value.val),
                'gamma': np.squeeze(nodes[4].value.val) / np.squeeze(nodes[2].value.val),
                'beta': np.squeeze(nodes[6].value.val),
            }

        fused_bn_node.datatype = current_node.datatype
        graph[fused_bn_node.name] = fused_bn_node

        # combine control i/o
        control_inputs = list()
        control_outputs = list()
        bn_node_names = [x.name for x in nodes]
        for name in bn_node_names:
            control_inputs += graph[name].control_inputs
            control_outputs += graph[name].control_outputs
        fused_bn_node.control_inputs.extend(control_inputs)
        fused_bn_node.control_outputs.extend(control_outputs)

        # connect fused node to entry and output nodes
        connect_edge(graph, current_node.name, fused_bn_node.name)
        connect_dests(graph, fused_bn_node.name, bn_outputs)

        # correct output's inputs order
        for out in bn_outputs:
            if len(graph[out].inputs) < 2:
                continue
            out_inputs = graph[out].inputs
            a = out_inputs.index(out_node.name)
            b = out_inputs.index(fused_bn_node.name)
            out_inputs[a], out_inputs[b] = out_inputs[b], out_inputs[a]

        # delete merged nodes
        for name in bn_node_names:
            delete_node(graph, name)