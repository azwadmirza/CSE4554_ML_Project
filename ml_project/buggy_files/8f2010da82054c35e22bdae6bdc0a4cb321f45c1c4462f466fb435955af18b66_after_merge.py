def _validate_unique_outputs(nodes: List[Node]) -> None:
    outputs = chain.from_iterable(node.outputs for node in nodes)
    outputs = map(_get_transcode_compatible_name, outputs)
    duplicates = [key for key, value in Counter(outputs).items() if value > 1]
    if duplicates:
        raise OutputNotUniqueError(
            "Output(s) {} are returned by more than one nodes. Node "
            "outputs must be unique.".format(sorted(duplicates))
        )