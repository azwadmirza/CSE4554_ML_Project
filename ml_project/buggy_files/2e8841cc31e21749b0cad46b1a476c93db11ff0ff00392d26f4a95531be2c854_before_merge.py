async def _replace_edge_labels_with_nodes(
    graph, next_id, interpreter, nlu_training_data
):
    """User messages are created as edge labels. This removes the labels and
    creates nodes instead.

    The algorithms (e.g. merging) are simpler if the user messages are labels
    on the edges. But it sometimes
    looks better if in the final graphs the user messages are nodes instead
    of edge labels."""

    if nlu_training_data:
        message_generator = UserMessageGenerator(nlu_training_data)
    else:
        message_generator = None

    edges = list(graph.edges(keys=True, data=True))
    for s, e, k, d in edges:
        if k != EDGE_NONE_LABEL:
            if message_generator and d.get("label", k) is not None:
                parsed_info = await interpreter.parse(d.get("label", k))
                label = message_generator.message_for_data(parsed_info)
            else:
                label = d.get("label", k)
            next_id += 1
            graph.remove_edge(s, e, k)
            graph.add_node(
                next_id,
                label=label,
                shape="rect",
                style="filled",
                fillcolor="lightblue",
                **_transfer_style(d, {"class": "intent"})
            )
            graph.add_edge(s, next_id, **{"class": d.get("class", "")})
            graph.add_edge(next_id, e, **{"class": d.get("class", "")})