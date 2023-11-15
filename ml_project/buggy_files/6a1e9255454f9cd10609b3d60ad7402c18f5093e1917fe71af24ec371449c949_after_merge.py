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