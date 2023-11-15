def fuse_batch_norm(ssa):
    """
    A graph pass that match and fuses following op patterns into a single BatchNorm op.

    Pattern 1:
             [Const]   [Const]
                |         |
                V         V
    [...] --> [Mul] --> [Add] --> [...] to [...] --> [BatchNorm] --> [...]

    Pattern 2:
             [Const]   [Const]   [Const]
                |         |         |
                V         V         V
    [...] --> [Sub] --> [Mul] --> [Add] --> [...] to [...] --> [BatchNorm] --> [...]

    Pattern 3:
             [Const]   [Const]       [Const]     [Const]
                |         |            |            |
                V         V            V            V
    [...] --> [Sub] --> [RealDiv] --> [Mul] --> [BiasAdd] --> [...] to [...] --> [BatchNorm] --> [...]
    """

    def _match_batch_norm_pattern(graph, entry_node, pattern_ops):
        if not _check_number_outputs(entry_node, 1):
            return None
        nodes_to_merge = list()
        node = graph[entry_node.outputs[0]]
        for i, op in enumerate(pattern_ops):
            if node.op != op:
                return None
            if node.op != pattern_ops[i] and not _check_number_outputs(node, 1):
                return None
            if not _check_number_inputs(node, 2):
                return None
            const_node = graph[node.inputs[1]]
            if not _check_single_out_vector_constant_node(const_node):
                return None
            if not _check_rank_matches(const_node, node):
                return None
            nodes_to_merge.extend([const_node, node])
            if len(node.outputs) == 0:  # do not fuse the output layer
                return None
            node = graph[node.outputs[0]]
        if len(nodes_to_merge) != len(pattern_ops) * 2:
            return None
        return nodes_to_merge

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

    def _fuse_batch_norm(graph):
        keys = list(graph.keys())
        count = 0
        for k in keys:
            if k not in graph:
                continue
            current_node = graph[k]

            # return nodes order: [Const, Sub, Const, RealDiv, Const, Mul, Const, BiasAdd]
            nodes3 = _match_batch_norm_pattern(graph, current_node, ['Sub', 'RealDiv', 'Mul', 'BiasAdd'])
            # return nodes order: : [Const, Sub, Const, Mul, Const, Add]
            nodes2 = _match_batch_norm_pattern(graph, current_node, ['Sub', 'Mul', 'Add'])
            # return nodes order: : [Const, Mul, Const, Add]
            nodes1 = _match_batch_norm_pattern(graph, current_node, ['Mul', 'Add'])

            if nodes3:
                _merge_batch_norm(graph, nodes=nodes3, pattern_id=3)
                count += len(nodes3)

            if nodes2:
                _merge_batch_norm(graph, nodes=nodes2, pattern_id=2)
                count += len(nodes2)

            if nodes1:
                _merge_batch_norm(graph, nodes=nodes1, pattern_id=1)
                count += len(nodes1)

        if count > 0:
            print('[Op Fusion] Fused {} nodes into BatchNorms.'.format(count))

    for fn_key in list(ssa.functions.keys()):
        f = ssa.functions[fn_key]
        _fuse_batch_norm(f.graph)