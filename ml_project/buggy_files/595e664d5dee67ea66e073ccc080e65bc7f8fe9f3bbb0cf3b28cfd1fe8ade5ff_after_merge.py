def _construct_divmod_result(left, result, index, name, dtype=None):
    """divmod returns a tuple of like indexed series instead of a single series.
    """
    return (
        _construct_result(left, result[0], index=index, name=name,
                          dtype=dtype),
        _construct_result(left, result[1], index=index, name=name,
                          dtype=dtype),
    )