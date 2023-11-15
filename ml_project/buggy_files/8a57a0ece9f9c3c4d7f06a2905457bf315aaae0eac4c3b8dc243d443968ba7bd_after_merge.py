def _connected_by_alternating_paths(G, matching, targets):
    """Returns the set of vertices that are connected to one of the target
    vertices by an alternating path in `G` or are themselves a target.

    An *alternating path* is a path in which every other edge is in the
    specified maximum matching (and the remaining edges in the path are not in
    the matching). An alternating path may have matched edges in the even
    positions or in the odd positions, as long as the edges alternate between
    'matched' and 'unmatched'.

    `G` is an undirected bipartite NetworkX graph.

    `matching` is a dictionary representing a maximum matching in `G`, as
    returned by, for example, :func:`maximum_matching`.

    `targets` is a set of vertices.

    """
    # Get the set of matched edges and the set of unmatched edges. Only include
    # one version of each undirected edge (for example, include edge (1, 2) but
    # not edge (2, 1)). Using frozensets as an intermediary step we do not
    # require nodes to be orderable.
    edge_sets = {frozenset((u, v)) for u, v in matching.items()}
    matched_edges = {tuple(edge) for edge in edge_sets}
    unmatched_edges = {(u, v) for (u, v) in G.edges()
                       if frozenset((u, v)) not in edge_sets}

    return {v for v in G if v in targets or
            _is_connected_by_alternating_path(G, v, matched_edges,
                                              unmatched_edges, targets)}