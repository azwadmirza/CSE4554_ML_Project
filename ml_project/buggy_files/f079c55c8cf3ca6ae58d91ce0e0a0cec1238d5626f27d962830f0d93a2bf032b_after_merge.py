def backfill_2d(values, limit=None, mask=None):
    if is_float_dtype(values):
        _method = _algos.backfill_2d_inplace_float64
    elif is_datetime64_dtype(values):
        _method = _backfill_2d_datetime
    elif values.dtype == np.object_:
        _method = _algos.backfill_2d_inplace_object
    else: # pragma: no cover
        raise ValueError('Invalid dtype for padding')

    if mask is None:
        mask = isnull(values)
    mask = mask.view(np.uint8)

    if np.all(values.shape):
        _method(values, mask, limit=limit)
    else:
        # for test coverage
        pass