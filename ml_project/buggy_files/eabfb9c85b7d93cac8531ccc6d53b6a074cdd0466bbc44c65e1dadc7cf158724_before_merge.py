def _remove_internal_identity_nodes(nnssa):
    '''
    remove identity nodes that are not connected to the model outputs
    '''
    delete_count = 0
    for fn_key in list(nnssa.functions.keys()):
        f = nnssa.functions[fn_key]
        keys = list(f.graph.keys())
        for k in keys:
            if k not in f.graph:
                continue
            node = f.graph[k]
            if len(node.inputs) != 1 or len(node.outputs) != 1:
                continue
            inp_node = f.graph[node.inputs[0]]
            if node.op == 'Identity' and inp_node.op != 'get_tuple':
                delete_count += 1
                parent_name = f.graph[k].inputs[0]
                disconnect_edge(f.graph, parent_name, k)
                for control_input in f.graph[k].control_inputs:
                    replace_control_dest(f.graph, control_input, k, parent_name)

                replace_node(f.graph, k, parent_name)  # join parent to children
                delete_node(f.graph, k)

    return delete_count