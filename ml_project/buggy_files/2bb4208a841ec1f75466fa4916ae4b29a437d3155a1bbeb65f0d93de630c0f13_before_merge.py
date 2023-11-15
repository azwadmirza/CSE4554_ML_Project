    def build_graph(self, graph=None, cls=DAG, tiled=False, compose=True, executed_keys=None):
        from .tensor.expressions.utils import convert_to_fetch

        executed_keys = executed_keys or []
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
            node = nodes.pop()

            # replace executed tensor/chunk by tensor/chunk with fetch op
            if node.key in executed_keys:
                node = convert_to_fetch(node).data

            visited.add(node)
            if not graph.contains(node):
                graph.add_node(node)
            children = node.inputs or []
            for c in children:
                if c.key in executed_keys:
                    continue
                if not graph.contains(c):
                    graph.add_node(c)
                if not graph.has_successor(c, node):
                    graph.add_edge(c, node)
            nodes.extend([c for c in itertools.chain(*[inp.op.outputs for inp in node.inputs or []])
                          if c not in visited])
        if tiled and compose:
            graph.compose(keys=keys)
        return graph