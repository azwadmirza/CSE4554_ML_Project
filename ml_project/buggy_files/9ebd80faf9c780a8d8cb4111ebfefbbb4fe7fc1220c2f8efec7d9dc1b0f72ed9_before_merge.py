def create_image_reader(filename):
    """Return a ``gdcm.ImageReader``.

    Parameters
    ----------
    filename: str or unicode
        The path to the DICOM dataset.

    Returns
    -------
    gdcm.ImageReader
    """
    image_reader = gdcm.ImageReader()
    image_reader.SetFileName(filename)
    return image_reader