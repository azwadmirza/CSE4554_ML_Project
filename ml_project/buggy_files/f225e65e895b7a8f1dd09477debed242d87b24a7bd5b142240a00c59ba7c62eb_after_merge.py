def add_logo(orig, dc, img, logo=None):
    """Add logos or other images to an image using the pydecorate package.

    All the features of pydecorate's ``add_logo`` are available.
    See documentation of :doc:`pydecorate:index` for more info.

    """
    LOG.info("Add logo to image.")

    dc.add_logo(**logo)

    arr = da.from_array(np.array(img) / 255.0, chunks=CHUNK_SIZE)

    new_data = xr.DataArray(arr, dims=['y', 'x', 'bands'],
                            coords={'y': orig.data.coords['y'],
                                    'x': orig.data.coords['x'],
                                    'bands': list(img.mode)},
                            attrs=orig.data.attrs)
    return XRImage(new_data)