def _extract_bool_array(mask: ArrayLike) -> np.ndarray:
    """
    If we have a SparseArray or BooleanArray, convert it to ndarray[bool].
    """
    if isinstance(mask, ExtensionArray):
        # We could have BooleanArray, Sparse[bool], ...
        mask = np.asarray(mask, dtype=np.bool_)

    assert isinstance(mask, np.ndarray), type(mask)
    assert mask.dtype == bool, mask.dtype
    return mask