    def slice_graph(graph, node, frontier, include_frontier=False):
        """
        Generate a slice of the graph from the head node to the given frontier.

        :param networkx.DiGraph graph: The graph to work on.
        :param node: The starting node in the graph.
        :param frontier: A list of frontier nodes.
        :param bool include_frontier: Whether the frontier nodes are included in the slice or not.
        :return: A subgraph.
        :rtype: networkx.DiGraph
        """

        subgraph = networkx.DiGraph()

        for frontier_node in frontier:
            for simple_path in networkx.all_simple_paths(graph, node, frontier_node):
                for src, dst in zip(simple_path, simple_path[1:]):
                    if include_frontier or (src not in frontier and dst not in frontier):
                        subgraph.add_edge(src, dst)

        return subgraph