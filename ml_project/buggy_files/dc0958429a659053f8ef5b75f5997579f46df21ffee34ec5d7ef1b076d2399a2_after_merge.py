def get_pixeldata(dicom_dataset):
    """Use the GDCM package to decode *Pixel Data*.

    Returns
    -------
    numpy.ndarray
        A correctly sized (but not shaped) array of the entire data volume

    Raises
    ------
    ImportError
        If the required packages are not available.
    TypeError
        If the image could not be read by GDCM or if the *Pixel Data* type is
        unsupported.
    AttributeError
        If the decoded amount of data does not match the expected amount.
    """

    if not HAVE_GDCM:
        msg = ("GDCM requires both the gdcm package and numpy "
               "and one or more could not be imported")
        raise ImportError(msg)

    if HAVE_GDCM_IN_MEMORY_SUPPORT:
        gdcm_data_element = create_data_element(dicom_dataset)
        gdcm_image = create_image(dicom_dataset, gdcm_data_element)
    else:
        gdcm_image_reader = create_image_reader(dicom_dataset)
        if not gdcm_image_reader.Read():
            raise TypeError("GDCM could not read DICOM image")
        gdcm_image = gdcm_image_reader.GetImage()

    # GDCM returns char* as type str. Python 3 decodes this to
    # unicode strings by default.
    # The SWIG docs mention that they always decode byte streams
    # as utf-8 strings for Python 3, with the `surrogateescape`
    # error handler configured.
    # Therefore, we can encode them back to their original bytearray
    # representation on Python 3 by using the same parameters.

    pixel_bytearray = gdcm_image.GetBuffer().encode(
        "utf-8", "surrogateescape")

    # Here we need to be careful because in some cases, GDCM reads a
    # buffer that is too large, so we need to make sure we only include
    # the first n_rows * n_columns * dtype_size bytes.
    expected_length_bytes = get_expected_length(dicom_dataset)
    if dicom_dataset.PhotometricInterpretation == 'YBR_FULL_422':
        # GDCM has already resampled the pixel data, see PS3.3 C.7.6.3.1.2
        expected_length_bytes = expected_length_bytes // 2 * 3

    if len(pixel_bytearray) > expected_length_bytes:
        # We make sure that all the bytes after are in fact zeros
        padding = pixel_bytearray[expected_length_bytes:]
        if numpy.any(numpy.frombuffer(padding, numpy.byte)):
            pixel_bytearray = pixel_bytearray[:expected_length_bytes]
        else:
            # We revert to the old behavior which should then result
            #   in a Numpy error later on.
            pass

    numpy_dtype = pixel_dtype(dicom_dataset)
    pixel_array = numpy.frombuffer(pixel_bytearray, dtype=numpy_dtype)

    expected_length_pixels = get_expected_length(dicom_dataset, 'pixels')
    if pixel_array.size != expected_length_pixels:
        raise AttributeError("Amount of pixel data %d does "
                             "not match the expected data %d" %
                             (pixel_array.size, expected_length_pixels))

    if should_change_PhotometricInterpretation_to_RGB(dicom_dataset):
        dicom_dataset.PhotometricInterpretation = "RGB"

    return pixel_array.copy()