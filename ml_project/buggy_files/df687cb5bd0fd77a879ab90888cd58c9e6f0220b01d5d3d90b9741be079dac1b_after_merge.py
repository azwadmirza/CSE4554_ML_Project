    def add_edge(self, src, dest, data=None):
        """
        Add an edge from node *src* to node *dest*, with optional
        per-edge *data*.
        If such an edge already exists, it is replaced (duplicate edges
        are not possible).
        """
        if src not in self._nodes:
            raise ValueError("Cannot add edge as src node %s not in nodes %s" %
                             (src, self._nodes))
        if dest not in self._nodes:
            raise ValueError("Cannot add edge as dest node %s not in nodes %s" %
                             (dest, self._nodes))
        self._add_edge(src, dest, data)