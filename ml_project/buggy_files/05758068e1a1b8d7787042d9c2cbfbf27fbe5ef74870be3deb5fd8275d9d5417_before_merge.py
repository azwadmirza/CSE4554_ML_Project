def to_image(dataset, copy=True, **kwargs):
    # Only add keywords if they are present
    for key in ["mode", "fill_value", "palette"]:
        if key in dataset.info:
            kwargs.setdefault(key, dataset.info[key])

    if dataset.ndim == 2:
        return Image([dataset], copy=copy, **kwargs)
    elif dataset.ndim == 3:
        return Image([band for band in dataset], copy=copy, **kwargs)
    else:
        raise ValueError(
            "Don't know how to convert array with ndim %d to image" %
            dataset.ndim)