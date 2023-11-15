def _extract_bool_array(mask: ArrayLike) -> np.ndarray:
    """
    If we have a SparseArray or BooleanArray, convert it to ndarray[bool].
    """
    if isinstance(mask, ExtensionArray):
        # We could have BooleanArray, Sparse[bool], ...
        #  Except for BooleanArray, this is equivalent to just
        #  np.asarray(mask, dtype=bool)
        mask = mask.to_numpy(dtype=bool, na_value=False)

    assert isinstance(mask, np.ndarray), type(mask)
    assert mask.dtype == bool, mask.dtype
    return mask