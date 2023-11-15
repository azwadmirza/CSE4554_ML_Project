    def _alternating_dfs(u, depth, along_matched=True):
        """Returns True if and only if `u` is connected to one of the
        targets by an alternating path.

        `u` is a vertex in the graph `G`.

        `depth` specifies the maximum recursion depth of the depth-first
        search.

        If `along_matched` is True, this step of the depth-first search
        will continue only through edges in the given matching. Otherwise, it
        will continue only through edges *not* in the given matching.

        """
        # Base case 1: u is one of the target vertices. `u` is connected to one
        # of the target vertices by an alternating path of length zero.
        if u in targets:
            return True
        # Base case 2: we have exceeded are allowed depth. In this case, we
        # have looked at a path of length `n`, so looking any further won't
        # help.
        if depth < 0:
            return False
        # Determine which set of edges to look across.
        valid_edges = matched_edges if along_matched else unmatched_edges
        for v in G[u]:
            # Consider only those neighbors connected via a valid edge.
            if (u, v) in valid_edges or (v, u) in valid_edges:
                # Recursively perform a depth-first search starting from the
                # neighbor. Decrement the depth limit and switch which set of
                # vertices will be valid for next time.
                return _alternating_dfs(v, depth - 1, not along_matched)
        # If there are no more vertices to look through and we haven't yet
        # found a target vertex, simply say that no path exists.
        return False