def _remove_output_identity_nodes(nnssa):
    '''
    remove identity nodes that ARE connected to the model outputs
    '''
    delete_count = 0
    for fn_key in list(nnssa.functions.keys()):
        f = nnssa.functions[fn_key]
        keys = list(f.graph.keys())
        for k in keys:
            if k not in f.graph:
                continue
            node = f.graph[k]

            if node.op != 'Identity' or len(node.inputs) != 1:
                continue

            if len(node.outputs) != 0 or (k not in f.outputs) or k != node.name:
                continue
            # this means node k is the "output-identity" node that nnssa inserts
            # we remove it here
            parent_name = node.inputs[0]
            parent_node = f.graph[parent_name]

            # Continue if parent node has an other outputs than identity node.
            if any([an_output != k for an_output in parent_node.outputs]):
                continue

            delete_count += 1

            # Remove Identity node and copy existing parent node
            parent_node = copy.deepcopy(f.graph[parent_name])
            for control_input_name in node.control_inputs:
                if control_input_name == parent_node.name:
                    continue
                if control_input_name in parent_node.control_inputs:
                    continue

                parent_node.control_inputs.append(control_input_name)

            del f.graph[k]
            del f.graph[parent_name]
            parent_node.name = k
            parent_node.outputs = []
            f.graph[k] = parent_node

            node = f.graph[k]
            for p in node.inputs:
                for idx, out in enumerate(f.graph[p].outputs):
                    if out == parent_name:
                        f.graph[p].outputs[idx] = k

            for p in node.control_inputs:
                for idx, out in enumerate(f.graph[p].control_outputs):
                    if out == parent_name:
                        f.graph[p].control_outputs[idx] = k

    return delete_count