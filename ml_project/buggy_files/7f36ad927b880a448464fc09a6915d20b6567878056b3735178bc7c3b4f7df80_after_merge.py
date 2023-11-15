def get_size(item):
    """Return shape/size/len of an item of arbitrary type"""
    try:
        if hasattr(item, 'shape') and isinstance(item.shape, (tuple, integer)):
            try:
                if item.shape:
                    return item.shape
                else:
                    # Scalar value
                    return 1
            except RecursionError:
                # This is necessary to avoid an error when trying to
                # get the shape of these objects.
                # Fixes spyder-ide/spyder-kernels#217
                return (-1, -1)
        elif hasattr(item, 'size') and isinstance(item.size, (tuple, integer)):
            try:
                return item.size
            except RecursionError:
                return (-1, -1)
        elif hasattr(item, '__len__'):
            return len(item)
        else:
            return 1
    except Exception:
        # There is one item
        return 1