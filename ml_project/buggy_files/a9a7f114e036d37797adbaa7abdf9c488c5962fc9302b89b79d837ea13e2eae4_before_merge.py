def _encode_zarr_attr_value(value):
    if isinstance(value, np.ndarray):
        encoded = value.tolist()
    # this checks if it's a scalar number
    elif isinstance(value, np.generic):
        encoded = value.item()
        # np.string_('X').item() returns a type `bytes`
        # zarr still doesn't like that
        if type(encoded) is bytes:  # noqa
            encoded = b64encode(encoded)
    else:
        encoded = value
    return encoded