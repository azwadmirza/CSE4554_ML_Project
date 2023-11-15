def add_text(orig, dc, img, text=None):
    """Add text to an image using the pydecorate package.

    All the features of pydecorate's ``add_text`` are available.
    See documentation of :doc:`pydecorate:index` for more info.

    """
    LOG.info("Add text to image.")

    dc.add_text(**text)

    arr = da.from_array(np.array(img) / 255.0, chunks=CHUNK_SIZE)

    new_data = xr.DataArray(arr, dims=['y', 'x', 'bands'],
                            coords={'y': orig.data.coords['y'],
                                    'x': orig.data.coords['x'],
                                    'bands': list(img.mode)},
                            attrs=orig.data.attrs)
    return XRImage(new_data)