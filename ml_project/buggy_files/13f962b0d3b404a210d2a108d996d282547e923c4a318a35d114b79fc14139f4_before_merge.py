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
            if f.graph[k].op == 'Identity' and len(f.graph[k].inputs) == 1:
                if len(f.graph[k].outputs) == 0 and (k in f.outputs) and k == f.graph[k].name:
                    # this means node k is the "output-identity" node that nnssa inserts
                    # we remove it here
                    delete_count += 1
                    parent_name = f.graph[k].inputs[0]
                    f.graph[parent_name].control_outputs = f.graph[k].control_outputs

                    if any([ an_output != k for an_output in f.graph[parent_name].outputs]):
                        continue

                    del f.graph[k]
                    f.graph[k] = copy.deepcopy(f.graph[parent_name])
                    del f.graph[parent_name]
                    f.graph[k].name = k
                    f.graph[k].outputs = []

                    for p in f.graph[k].inputs:
                        for idx, out in enumerate(f.graph[p].outputs):
                            if out == parent_name:
                                f.graph[p].outputs[idx] = k

                    for p in f.graph[k].control_inputs:
                        for idx, out in enumerate(f.graph[p].control_outputs):
                            if out == parent_name:
                                f.graph[p].control_outputs[idx] = k
    return delete_count