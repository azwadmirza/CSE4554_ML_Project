def get_size(item):
    """Return size of an item of arbitrary type"""
    if isinstance(item, (list, set, tuple, dict)):
        return len(item)
    elif isinstance(item, (ndarray, MaskedArray)):
        return item.shape
    elif isinstance(item, Image):
        return item.size
    if isinstance(item, (DataFrame, Index, Series)):
        try:
            return item.shape
        except RecursionError:
            # This is necessary to avoid an error when trying to
            # get the shape of these objects.
            # Fixes spyder-ide/spyder-kernels#217
            return (-1, -1)
    else:
        return 1