def _graph_connected_component(graph, node_id):
    """Find the largest graph connected components the contains one
    given node

    Parameters
    ----------
    graph : array-like, shape: (n_samples, n_samples)
        adjacency matrix of the graph, non-zero weight means an edge
        between the nodes

    node_id : int
        The index of the query node of the graph

    Returns
    -------
    connected_components_matrix : array-like, shape: (n_samples,)
        An array of bool value indicates the indexes of the nodes
        belong to the largest connected components of the given query
        node
    """
    connected_components_matrix = np.zeros(shape=(graph.shape[0]), dtype=np.bool)
    connected_components_matrix[node_id] = True
    n_node = graph.shape[0]
    for i in range(n_node):
        last_num_component = connected_components_matrix.sum()
        _, node_to_add = np.where(graph[connected_components_matrix] != 0)
        connected_components_matrix[node_to_add] = True
        if last_num_component >= connected_components_matrix.sum():
            break
    return connected_components_matrix