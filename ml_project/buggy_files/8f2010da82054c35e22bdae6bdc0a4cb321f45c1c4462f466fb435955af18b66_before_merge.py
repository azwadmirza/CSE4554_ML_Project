def _validate_unique_outputs(nodes: List[Node]) -> None:
    outputs_list = list(chain.from_iterable(node.outputs for node in nodes))
    outputs_list = [_get_transcode_compatible_name(o) for o in outputs_list]
    counter_list = Counter(outputs_list)
    counter_set = Counter(set(outputs_list))
    diff = counter_list - counter_set
    if diff:
        raise OutputNotUniqueError(
            "Output(s) {} are returned by "
            "more than one nodes. Node "
            "outputs must be unique.".format(sorted(diff.keys()))
        )