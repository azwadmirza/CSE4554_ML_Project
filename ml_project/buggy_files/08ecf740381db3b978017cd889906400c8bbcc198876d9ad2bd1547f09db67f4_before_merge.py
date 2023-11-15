def sorted_topologically(
    nodes: Iterable[T], graph: Mapping[T, Collection[T]],
) -> Generator[T, None, None]:
    """Given a set of nodes and a graph, yield the nodes in toplogical order.

    For example `sorted_topologically([1, 2], {1: [2]})` will yield `2, 1`.
    """

    # This is implemented by Kahn's algorithm.

    degree_map = {node: 0 for node in nodes}
    reverse_graph = {}  # type: Dict[T, Set[T]]

    for node, edges in graph.items():
        if node not in degree_map:
            continue

        for edge in edges:
            if edge in degree_map:
                degree_map[node] += 1

            reverse_graph.setdefault(edge, set()).add(node)
        reverse_graph.setdefault(node, set())

    zero_degree = [node for node, degree in degree_map.items() if degree == 0]
    heapq.heapify(zero_degree)

    while zero_degree:
        node = heapq.heappop(zero_degree)
        yield node

        for edge in reverse_graph.get(node, []):
            if edge in degree_map:
                degree_map[edge] -= 1
                if degree_map[edge] == 0:
                    heapq.heappush(zero_degree, edge)