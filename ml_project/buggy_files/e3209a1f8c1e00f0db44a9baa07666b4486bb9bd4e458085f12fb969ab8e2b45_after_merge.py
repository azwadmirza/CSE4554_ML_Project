def calc_data_size(dt):
    if dt is None:
        return 0

    if isinstance(dt, tuple):
        return sum(calc_data_size(c) for c in dt)

    if hasattr(dt, 'nbytes'):
        return max(sys.getsizeof(dt), dt.nbytes)
    if hasattr(dt, 'shape') and len(dt.shape) == 0:
        return 0
    if hasattr(dt, 'memory_usage') or hasattr(dt, 'groupby_obj'):
        return sys.getsizeof(dt)
    if hasattr(dt, 'dtypes') and hasattr(dt, 'shape'):
        return dt.shape[0] * sum(dtype.itemsize for dtype in dt.dtypes)
    if hasattr(dt, 'dtype') and hasattr(dt, 'shape'):
        return dt.shape[0] * dt.dtype.itemsize

    # object chunk
    return sys.getsizeof(dt)