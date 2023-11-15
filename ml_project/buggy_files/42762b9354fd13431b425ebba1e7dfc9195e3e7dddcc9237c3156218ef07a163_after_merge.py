def _add_message_edge(
    graph: "networkx.MultiDiGraph",
    message: Dict[Text, Any],
    current_node: int,
    next_node_idx: int,
    is_current: bool,
):
    """Create an edge based on the user message."""

    if message:
        message_key = message.get("intent", {}).get("name", None)
        message_label = message.get("text", None)
    else:
        message_key = None
        message_label = None

    _add_edge(
        graph,
        current_node,
        next_node_idx,
        message_key,
        message_label,
        **{"class": "active" if is_current else ""}
    )