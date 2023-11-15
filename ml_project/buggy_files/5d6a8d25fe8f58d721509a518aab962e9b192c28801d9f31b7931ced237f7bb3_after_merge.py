    def build_graph(self, graph=None, cls=DAG, tiled=False, compose=True):
        if tiled and self.is_coarse():
            self.tiles()

        graph = graph if graph is not None else cls()
        keys = None

        if tiled:
            nodes = list(c.data for c in self.chunks)
            keys = list(c.key for c in self.chunks)
        else:
            nodes = list(self.op.outputs)
        visited = set()
        while len(nodes) > 0:
            chunk = nodes.pop()
            visited.add(chunk)
            if not graph.contains(chunk):
                graph.add_node(chunk)
            children = chunk.inputs or []
            for c in children:
                if not graph.contains(c):
                    graph.add_node(c)
                if not graph.has_successor(c, chunk):
                    graph.add_edge(c, chunk)
            nodes.extend([c for c in children if c not in visited])
        if tiled and compose:
            graph.compose(keys=keys)
        return graph