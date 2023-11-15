def sort(
    graph: Mapping[K, DepGraphEntry[K, V, T]],
    *,
    allow_unresolved: bool = False,
) -> Iterator[V]:
    items = sort_ex(graph, allow_unresolved=allow_unresolved)
    return (i[1].item for i in items)