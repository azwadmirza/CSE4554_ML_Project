def _apply_mask(data,  # type: np.ndarray
                encoded_fill_values,  # type: list
                decoded_fill_value  # type: Any
                ):  # type: npndarray
    """Mask all matching values in a NumPy arrays."""
    condition = False
    for fv in encoded_fill_values:
        condition |= data == fv
    return np.where(condition, decoded_fill_value, data)