def visualize_neighborhood(
    current: Optional[List[Event]],
    event_sequences: List[List[Event]],
    output_file: Optional[Text] = None,
    max_history: int = 2,
    interpreter: NaturalLanguageInterpreter = RegexInterpreter(),
    nlu_training_data: Optional[TrainingData] = None,
    should_merge_nodes: bool = True,
    max_distance: int = 1,
    fontsize: int = 12
):
    """Given a set of event lists, visualizing the flows."""

    graph = _create_graph(fontsize)
    _add_default_nodes(graph)

    next_node_idx = START_NODE_ID
    special_node_idx = -3
    path_ellipsis_ends = set()

    for events in event_sequences:
        if current and max_distance:
            prefix = _length_of_common_action_prefix(current, events)
        else:
            prefix = len(events)

        message = None
        current_node = START_NODE_ID
        idx = 0
        is_current = events == current

        for idx, el in enumerate(events):
            if not prefix:
                idx -= 1
                break
            if isinstance(el, UserUttered):
                if not el.intent:
                    message = interpreter.parse(el.text)
                else:
                    message = el.parse_data
            elif (isinstance(el, ActionExecuted) and
                  el.action_name != ACTION_LISTEN_NAME):
                next_node_idx += 1
                graph.add_node(next_node_idx,
                               label=el.action_name,
                               fontsize=fontsize,
                               **{"class": "active" if is_current else ""})

                _add_message_edge(graph, message, current_node, next_node_idx,
                                  is_current)
                current_node = next_node_idx

                message = None
                prefix -= 1

        # determine what the end node of the conversation is going to be
        # this can either be an ellipsis "...", the conversation end node
        # "END" or a "TMP" node if this is the active conversation
        if is_current:
            if (isinstance(events[idx], ActionExecuted) and
                    events[idx].action_name == ACTION_LISTEN_NAME):
                next_node_idx += 1
                graph.add_node(next_node_idx,
                               label=message or "  ?  ",
                               shape="rect",
                               **{"class": "intent dashed active"})
                target = next_node_idx
            elif current_node:
                d = graph.nodes(data=True)[current_node]
                d["class"] = "dashed active"
                target = TMP_NODE_ID
            else:
                target = TMP_NODE_ID
        elif idx == len(events) - 1:
            target = END_NODE_ID
        elif current_node and current_node not in path_ellipsis_ends:
            graph.add_node(special_node_idx, label="...",
                           **{"class": "ellipsis"})
            target = special_node_idx
            path_ellipsis_ends.add(current_node)
            special_node_idx -= 1
        else:
            target = END_NODE_ID

        _add_message_edge(graph, message, current_node, target, is_current)

    if should_merge_nodes:
        _merge_equivalent_nodes(graph, max_history)
    _replace_edge_labels_with_nodes(graph, next_node_idx, interpreter,
                                    nlu_training_data)

    _remove_auxiliary_nodes(graph, special_node_idx)

    if output_file:
        persist_graph(graph, output_file)
    return graph