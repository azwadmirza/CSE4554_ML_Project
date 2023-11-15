    def _find_initial_loop_nodes(self, graph, head):
        # TODO optimize
        latching_nodes = set([s for s,t in dfs_back_edges(graph, self._start_node) if t == head])
        loop_subgraph = self.slice_graph(graph, head, latching_nodes, include_frontier=True)
        nodes = set(loop_subgraph.nodes())
        return nodes