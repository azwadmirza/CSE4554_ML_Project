def transform_nhwc_to_nchw(nnssa):
    """
    Mark each one of the node with "NHWC", so that the conversion process
    could avoid inserting unnecessary transpositions.
    A node's format is "NHWC" if and only if:
    (1) it is a conv or pooling or image_resize layer with "NHWC" data format
    (2) it is a rank-preserving operation whose inputs are all "NHWC"
    """
    for fn_key in list(nnssa.functions.keys()):
        graph = nnssa.functions[fn_key].graph
        # this pass needs the ssa to be in the topologically sorted order
        node_names = topsort(graph)

        # Mark all NHWC nodes
        nhwc_nodes = []
        for name in node_names:
            node = graph[name]
            if len(node.outputs) > 0 and len(node.inputs) > 0 and _is_NHWC(graph, node):
                node.attr['data_format'] = 'NHWC_format_inserted'
                nhwc_nodes.append(name)

        for name in nhwc_nodes:

            node = graph[name]

            # Adjust type inference
            if builtins.is_tensor(node.datatype):
                s = node.datatype.get_shape()
                if len(s) == 4:
                    new_shape = tuple([s[0], s[3], s[1], s[2]])
                    node.datatype = builtins.tensor(node.datatype.get_primitive(), new_shape)
                    node.attr['symbolic_datatype'] = node.datatype

            if '_output_shapes' in node.attr:
                orig_out_shapes = node.attr['_output_shapes']
                if len(orig_out_shapes) == 1 and len(orig_out_shapes[0]) == 4:
                    s = orig_out_shapes[0]
                    node.attr['_output_shapes'] = [[s[0], s[3], s[1], s[2]]]

            if node.op in ELEMENTWISE_OPS:
                for inp in node.inputs:
                    parent_node = graph[inp]
                    if parent_node.value is not None:
                        # if there is a constant vector input
                        val = np.array(parent_node.value.val)
                        if len(val.shape) == 1 and builtins.is_tensor(parent_node.datatype):
                            new_shape = (1, val.shape[0], 1, 1)
                            parent_node.datatype = builtins.tensor(parent_node.datatype.get_primitive(), new_shape)
                            parent_node.value.val = np.reshape(parent_node.value.val, new_shape)

            # Insert NHWC -> NCHW transpose
            for i, inp_node_name in enumerate(node.inputs):
                inp_node_format = graph[inp_node_name].attr.get('data_format')
                symbolic_value = graph[inp_node_name].attr['symbolic_value']
                if (graph[inp_node_name].op == 'Const' or
                    len(graph[inp_node_name].datatype.get_shape()) != 4 or
                    ( symbolic_value and not any_symbolic_or_unknown(symbolic_value))):
                    # Const weights and parameters
                    continue
            
                if inp_node_format != 'NHWC_format_inserted':
                    assert len(graph[inp_node_name].datatype.get_shape()) == 4
                    _insert_transpose_to_nchw(graph, graph[inp_node_name], node)

            # Insert NCHW -> NHWC transpose
            for i, out_node_name in enumerate(node.outputs):
                out_node_format = graph[out_node_name].attr.get('data_format')
                if out_node_format != 'NHWC_format_inserted':
                    _insert_transpose_from_nchw(graph, node, graph[out_node_name])

            # Adjust output shape and concat layer's axis parameter
            if node.op == 'Concat' and len(node.inputs) > 1 and graph[node.inputs[0]].value is not None:
                axis = graph[node.inputs[0]].value.val
                axis = 4 + axis if axis < 0 else axis
                if axis == 3:
                    node.attr['axis'] = 1
                elif axis == 2 or axis == 1:
                    node.attr['axis'] = axis + 1
                else:
                    node.attr['axis'] = axis

            if node.op == 'ConcatV2' and len(node.inputs) > 1 and graph[node.inputs[-1]].value is not None:
                axis = graph[node.inputs[-1]].value.val
                axis = 4 + axis if axis < 0 else axis
                if axis == 3:
                    node.attr['axis'] = 1
                elif axis == 2 or axis == 1:
                    node.attr['axis'] = axis + 1
                else:
                    node.attr['axis'] = axis