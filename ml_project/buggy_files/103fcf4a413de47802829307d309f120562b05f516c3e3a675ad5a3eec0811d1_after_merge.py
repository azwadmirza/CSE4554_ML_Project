def _get_named_nodes_and_relations(graph, parent, leaf_nodes,
                                        node_parents, node_children):
    if getattr(graph, 'owner', None) is None:  # Leaf node
        if graph.name is not None:  # Named leaf node
            leaf_nodes.update({graph.name: graph})
            if parent is not None:  # Is None for the root node
                try:
                    node_parents[graph].add(parent)
                except KeyError:
                    node_parents[graph] = {parent}
                node_children[parent].add(graph)
            else:
                node_parents[graph] = set()
            # Flag that the leaf node has no children
            node_children[graph] = set()
    else:  # Intermediate node
        if graph.name is not None:  # Intermediate named node
            if parent is not None:  # Is only None for the root node
                try:
                    node_parents[graph].add(parent)
                except KeyError:
                    node_parents[graph] = {parent}
                node_children[parent].add(graph)
            else:
                node_parents[graph] = set()
            # The current node will be set as the parent of the next
            # nodes only if it is a named node
            parent = graph
            # Init the nodes children to an empty set
            node_children[graph] = set()
        for i in graph.owner.inputs:
            temp_nodes, temp_inter, temp_tree = \
                _get_named_nodes_and_relations(i, parent, leaf_nodes,
                                               node_parents, node_children)
            leaf_nodes.update(temp_nodes)
            node_parents.update(temp_inter)
            node_children.update(temp_tree)
    return leaf_nodes, node_parents, node_children