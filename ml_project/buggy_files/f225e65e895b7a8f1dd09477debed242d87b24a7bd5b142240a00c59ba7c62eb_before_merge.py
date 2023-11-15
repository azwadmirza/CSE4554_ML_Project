def add_logo(orig, dc, img, logo=None):
    """
    Add logos or other images to an image using the pydecorate function add_logo
    All the features in pydecorate are available

    See documentation of pydecorate
    """
    LOG.info("Add logo to image.")

    dc.add_logo(**logo)

    arr = da.from_array(np.array(img) / 255.0, chunks=CHUNK_SIZE)

    orig.data = xr.DataArray(arr, dims=['y', 'x', 'bands'],
                             coords={'y': orig.data.coords['y'],
                                     'x': orig.data.coords['x'],
                                     'bands': list(img.mode)},
                             attrs=orig.data.attrs)