def _remove_internal_identity_nodes(nnssa):
    '''
    remove identity nodes that are not connected to the model outputs
    '''
    delete_count = 0
    for fn_key in list(nnssa.functions.keys()):
        f = nnssa.functions[fn_key]
        for name in list(f.graph.keys()):
            if name not in f.graph:
                continue
            node = f.graph[name]

            # Check if the node is in graph outputs
            if len(node.inputs) != 1:
                continue
            if len(node.outputs) == 0 and len(node.control_outputs) == 0:
                continue

            # Remove identity node
            inp_node = f.graph[node.inputs[0]]
            if node.op == 'Identity' and inp_node.op != 'get_tuple':
                delete_count += 1
                parent_name = f.graph[name].inputs[0]
                disconnect_edge(f.graph, parent_name, name)
                for control_input in f.graph[name].control_inputs:
                    replace_control_dest(f.graph, control_input, name, parent_name)

                replace_node(f.graph, name, parent_name)  # join parent to children
                delete_node(f.graph, name)

    return delete_count