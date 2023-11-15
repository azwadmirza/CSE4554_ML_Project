def check_connections(gd):
    """
    Given a graph, checks that all 
     - inputs/outputs are symmetric
     - control_inputs/control_outputs are symmetric
     - The graph does not reference vertices outside of the graph

    Takes a graph in "dict{str, ParsedNode}" form. Does not return,
    asserts false on failure.
    """
    # check that inputs and outputs line up
    for k, v in gd.items():
        for i in v.inputs:
            assert (k in gd[i].outputs)
        for i in v.outputs:
            assert (k in gd[i].inputs)
        for i in v.control_inputs:
            assert (k in gd[i].control_outputs)
        for i in v.control_outputs:
            assert (k in gd[i].control_inputs)