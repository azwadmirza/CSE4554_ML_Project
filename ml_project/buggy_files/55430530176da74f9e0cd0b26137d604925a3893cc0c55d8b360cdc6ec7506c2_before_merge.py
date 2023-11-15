def _isna_new(obj):
    if is_scalar(obj):
        return libmissing.checknull(obj)
    # hack (for now) because MI registers as ndarray
    elif isinstance(obj, ABCMultiIndex):
        raise NotImplementedError("isna is not defined for MultiIndex")
    elif isinstance(
        obj,
        (
            ABCSeries,
            np.ndarray,
            ABCIndexClass,
            ABCExtensionArray,
            ABCDatetimeArray,
            ABCTimedeltaArray,
        ),
    ):
        return _isna_ndarraylike(obj)
    elif isinstance(obj, ABCGeneric):
        return obj._constructor(obj._data.isna(func=isna))
    elif isinstance(obj, list):
        return _isna_ndarraylike(np.asarray(obj, dtype=object))
    elif hasattr(obj, "__array__"):
        return _isna_ndarraylike(np.asarray(obj))
    else:
        return obj is None