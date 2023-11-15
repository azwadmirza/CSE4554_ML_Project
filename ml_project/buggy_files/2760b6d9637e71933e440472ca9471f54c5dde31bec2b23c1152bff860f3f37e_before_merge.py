def string_list_all_gather(strings: List[str], delimiter: str = "\t") -> List[str]:
    """
    Utility function for distributed data parallel to all gather a list of strings.

    Args:
        strings: a list of strings to all gather.
        delimiter: use the delimiter to join the string list to be a long string,
            then all gather across ranks and split to a list. default to "\t".

    """
    if idist.get_world_size() <= 1:
        return strings

    _joined = delimiter.join(strings)
    if get_torch_version_tuple() > (1, 6, 0):
        # all gather across all ranks
        _joined = delimiter.join(idist.all_gather(_joined))
    else:
        raise RuntimeError("MetricsSaver can not save metric details in distributed mode with PyTorch < 1.7.0.")

    return _joined.split(delimiter)