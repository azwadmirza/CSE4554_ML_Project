def to_image(dataset, copy=False, **kwargs):
    # Only add keywords if they are present
    for key in ["mode", "fill_value", "palette"]:
        if key in dataset.attrs:
            kwargs.setdefault(key, dataset.attrs[key])
    dataset = dataset.squeeze()

    if 'bands' in dataset.dims:
        return Image([np.ma.masked_invalid(dataset.sel(bands=band).values)
                      for band in dataset['bands']],
                     copy=copy, **kwargs)
    elif dataset.ndim < 2:
        raise ValueError("Need at least a 2D array to make an image.")
    else:
        return Image([np.ma.masked_invalid(dataset.values)], copy=copy, **kwargs)