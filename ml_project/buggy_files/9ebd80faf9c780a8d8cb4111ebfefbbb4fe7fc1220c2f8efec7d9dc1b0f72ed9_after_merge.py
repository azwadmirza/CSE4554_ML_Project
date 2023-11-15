def create_image_reader(ds):
    """Return a ``gdcm.ImageReader``.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The dataset to create the reader from.

    Returns
    -------
    gdcm.ImageReader
    """
    image_reader = gdcm.ImageReader()
    fname = getattr(ds, 'filename', None)
    if fname and isinstance(fname, str):
        pass
    else:
        # Copy the relevant elements and write to a temporary file to avoid
        #   having to deal with all the possible objects the dataset may
        #   originate with
        new = ds.group_dataset(0x0028)
        new["PixelData"] = ds["PixelData"]  # avoid ambiguous VR
        new.file_meta = ds.file_meta
        tfile = NamedTemporaryFile('wb')
        new.save_as(tfile.name)
        fname = tfile.name

    image_reader.SetFileName(fname)
    return image_reader