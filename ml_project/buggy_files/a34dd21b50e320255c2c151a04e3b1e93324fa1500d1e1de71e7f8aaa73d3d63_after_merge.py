def _is_connected_by_alternating_path(G, v, matched_edges, unmatched_edges,
                                      targets):
    """Returns True if and only if the vertex `v` is connected to one of
    the target vertices by an alternating path in `G`.

    An *alternating path* is a path in which every other edge is in the
    specified maximum matching (and the remaining edges in the path are not in
    the matching). An alternating path may have matched edges in the even
    positions or in the odd positions, as long as the edges alternate between
    'matched' and 'unmatched'.

    `G` is an undirected bipartite NetworkX graph.

    `v` is a vertex in `G`.

    `matched_edges` is a set of edges present in a maximum matching in `G`.

    `unmatched_edges` is a set of edges not present in a maximum
    matching in `G`.

    `targets` is a set of vertices.

    """
    def _alternating_dfs(u, along_matched=True):
        """Returns True if and only if `u` is connected to one of the
        targets by an alternating path.

        `u` is a vertex in the graph `G`.

        If `along_matched` is True, this step of the depth-first search
        will continue only through edges in the given matching. Otherwise, it
        will continue only through edges *not* in the given matching.

        """
        if along_matched:
            edges = itertools.cycle([matched_edges, unmatched_edges])
        else:
            edges = itertools.cycle([unmatched_edges, matched_edges])
        visited = set()
        stack = [(u, iter(G[u]), next(edges))]
        while stack:
            parent, children, valid_edges = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    if ((parent, child) in valid_edges
                            or (child, parent) in valid_edges):
                        if child in targets:
                            return True
                        visited.add(child)
                        stack.append((child, iter(G[child]), next(edges)))
            except StopIteration:
                stack.pop()
        return False

    # Check for alternating paths starting with edges in the matching, then
    # check for alternating paths starting with edges not in the
    # matching.
    return (_alternating_dfs(v, along_matched=True) or
            _alternating_dfs(v, along_matched=False))