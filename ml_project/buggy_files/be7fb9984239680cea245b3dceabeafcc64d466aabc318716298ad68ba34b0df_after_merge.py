def dcmwrite(filename, dataset, write_like_original=True):
    """Write `dataset` to the `filename` specified.

    If `write_like_original` is ``True`` then `dataset` will be written as is
    (after minimal validation checking) and may or may not contain all or parts
    of the File Meta Information (and hence may or may not be conformant with
    the DICOM File Format).

    If `write_like_original` is ``False``, `dataset` will be stored in the
    :dcm:`DICOM File Format <part10/chapter_7.html>`.  To do
    so requires that the ``Dataset.file_meta`` attribute
    exists and contains a :class:`Dataset` with the required (Type 1) *File
    Meta Information Group* elements. The byte stream of the `dataset` will be
    placed into the file after the DICOM *File Meta Information*.

    If `write_like_original` is ``True`` then the :class:`Dataset` will be
    written as is (after minimal validation checking) and may or may not
    contain all or parts of the *File Meta Information* (and hence may or
    may not be conformant with the DICOM File Format).

    **File Meta Information**

    The *File Meta Information* consists of a 128-byte preamble, followed by
    a 4 byte ``b'DICM'`` prefix, followed by the *File Meta Information Group*
    elements.

    **Preamble and Prefix**

    The ``dataset.preamble`` attribute shall be 128-bytes long or ``None`` and
    is available for use as defined by the Application Profile or specific
    implementations. If the preamble is not used by an Application Profile or
    specific implementation then all 128 bytes should be set to ``0x00``. The
    actual preamble written depends on `write_like_original` and
    ``dataset.preamble`` (see the table below).

    +------------------+------------------------------+
    |                  | write_like_original          |
    +------------------+-------------+----------------+
    | dataset.preamble | True        | False          |
    +==================+=============+================+
    | None             | no preamble | 128 0x00 bytes |
    +------------------+-------------+----------------+
    | 128 bytes        | dataset.preamble             |
    +------------------+------------------------------+

    The prefix shall be the bytestring ``b'DICM'`` and will be written if and
    only if the preamble is present.

    **File Meta Information Group Elements**

    The preamble and prefix are followed by a set of DICOM elements from the
    (0002,eeee) group. Some of these elements are required (Type 1) while
    others are optional (Type 3/1C). If `write_like_original` is ``True``
    then the *File Meta Information Group* elements are all optional. See
    :func:`~pydicom.filewriter.write_file_meta_info` for more information on
    which elements are required.

    The *File Meta Information Group* elements should be included within their
    own :class:`~pydicom.dataset.Dataset` in the ``dataset.file_meta``
    attribute.

    If (0002,0010) *Transfer Syntax UID* is included then the user must ensure
    its value is compatible with the values for the
    ``dataset.is_little_endian`` and ``dataset.is_implicit_VR`` attributes.
    For example, if ``is_little_endian`` and ``is_implicit_VR`` are both
    ``True`` then the Transfer Syntax UID must be 1.2.840.10008.1.2 *Implicit
    VR Little Endian*. See the DICOM Standard, Part 5,
    :dcm:`Section 10<part05/chapter_10.html>` for more information on Transfer
    Syntaxes.

    *Encoding*

    The preamble and prefix are encoding independent. The File Meta elements
    are encoded as *Explicit VR Little Endian* as required by the DICOM
    Standard.

    **Dataset**

    A DICOM Dataset representing a SOP Instance related to a DICOM Information
    Object Definition. It is up to the user to ensure the `dataset` conforms
    to the DICOM Standard.

    *Encoding*

    The `dataset` is encoded as specified by the ``dataset.is_little_endian``
    and ``dataset.is_implicit_VR`` attributes. It's up to the user to ensure
    these attributes are set correctly (as well as setting an appropriate
    value for ``dataset.file_meta.TransferSyntaxUID`` if present).

    Parameters
    ----------
    filename : str or PathLike or file-like
        Name of file or the file-like to write the new DICOM file to.
    dataset : pydicom.dataset.FileDataset
        Dataset holding the DICOM information; e.g. an object read with
        :func:`~pydicom.filereader.dcmread`.
    write_like_original : bool, optional
        If ``True`` (default), preserves the following information from
        the Dataset (and may result in a non-conformant file):

        - preamble -- if the original file has no preamble then none will be
          written.
        - file_meta -- if the original file was missing any required *File
          Meta Information Group* elements then they will not be added or
          written.
          If (0002,0000) *File Meta Information Group Length* is present then
          it may have its value updated.
        - seq.is_undefined_length -- if original had delimiters, write them now
          too, instead of the more sensible length characters
        - is_undefined_length_sequence_item -- for datasets that belong to a
          sequence, write the undefined length delimiters if that is
          what the original had.

        If ``False``, produces a file conformant with the DICOM File Format,
        with explicit lengths for all elements.

    Raises
    ------
    AttributeError
        If either ``dataset.is_implicit_VR`` or ``dataset.is_little_endian``
        have not been set.
    ValueError
        If group 2 elements are in ``dataset`` rather than
        ``dataset.file_meta``, or if a preamble is given but is not 128 bytes
        long, or if Transfer Syntax is a compressed type and pixel data is not
        compressed.

    See Also
    --------
    pydicom.dataset.FileDataset
        Dataset class with relevant attributes and information.
    pydicom.dataset.Dataset.save_as
        Write a DICOM file from a dataset that was read in with ``dcmread()``.
        ``save_as()`` wraps ``dcmwrite()``.
    """

    # Ensure is_little_endian and is_implicit_VR are set
    if None in (dataset.is_little_endian, dataset.is_implicit_VR):
        has_tsyntax = False
        try:
            tsyntax = dataset.file_meta.TransferSyntaxUID
            if not tsyntax.is_private:
                dataset.is_little_endian = tsyntax.is_little_endian
                dataset.is_implicit_VR = tsyntax.is_implicit_VR
                has_tsyntax = True
        except AttributeError:
            pass

        if not has_tsyntax:
            raise AttributeError(
                "'{0}.is_little_endian' and '{0}.is_implicit_VR' must be "
                "set appropriately before saving."
                .format(dataset.__class__.__name__)
            )

    # Try and ensure that `is_undefined_length` is set correctly
    try:
        tsyntax = dataset.file_meta.TransferSyntaxUID
        if not tsyntax.is_private:
            dataset['PixelData'].is_undefined_length = tsyntax.is_compressed
    except (AttributeError, KeyError):
        pass

    # Check that dataset's group 0x0002 elements are only present in the
    #   `dataset.file_meta` Dataset - user may have added them to the wrong
    #   place
    if dataset.group_dataset(0x0002) != Dataset():
        raise ValueError("File Meta Information Group Elements (0002,eeee) "
                         "should be in their own Dataset object in the "
                         "'{0}.file_meta' "
                         "attribute.".format(dataset.__class__.__name__))

    # A preamble is required under the DICOM standard, however if
    #   `write_like_original` is True we treat it as optional
    preamble = getattr(dataset, 'preamble', None)
    if preamble and len(preamble) != 128:
        raise ValueError("'{0}.preamble' must be 128-bytes "
                         "long.".format(dataset.__class__.__name__))
    if not preamble and not write_like_original:
        # The default preamble is 128 0x00 bytes.
        preamble = b'\x00' * 128

    # File Meta Information is required under the DICOM standard, however if
    #   `write_like_original` is True we treat it as optional
    if not write_like_original:
        # the checks will be done in write_file_meta_info()
        dataset.fix_meta_info(enforce_standard=False)
    else:
        dataset.ensure_file_meta()

    # Check for decompression, give warnings if inconsistencies
    # If decompressed, then pixel_array is now used instead of PixelData
    if dataset.is_decompressed:
        xfer = dataset.file_meta.TransferSyntaxUID
        if xfer not in UncompressedPixelTransferSyntaxes:
            raise ValueError("file_meta transfer SyntaxUID is compressed type "
                             "but pixel data has been decompressed")

        # Force PixelData to the decompressed version
        dataset.PixelData = dataset.pixel_array.tobytes()

    caller_owns_file = True
    # Open file if not already a file object
    filename = path_from_pathlike(filename)
    if isinstance(filename, str):
        fp = DicomFile(filename, 'wb')
        # caller provided a file name; we own the file handle
        caller_owns_file = False
    else:
        fp = DicomFileLike(filename)

    # if we want to write with the same endianess and VR handling as
    # the read dataset we want to preserve raw data elements for
    # performance reasons (which is done by get_item);
    # otherwise we use the default converting item getter
    if dataset.is_original_encoding:
        get_item = Dataset.get_item
    else:
        get_item = Dataset.__getitem__

    try:
        # WRITE FILE META INFORMATION
        if preamble:
            # Write the 'DICM' prefix if and only if we write the preamble
            fp.write(preamble)
            fp.write(b'DICM')

        if dataset.file_meta:  # May be an empty Dataset
            # If we want to `write_like_original`, don't enforce_standard
            write_file_meta_info(fp, dataset.file_meta,
                                 enforce_standard=not write_like_original)

        # WRITE DATASET
        # The transfer syntax used to encode the dataset can't be changed
        #   within the dataset.
        # Write any Command Set elements now as elements must be in tag order
        #   Mixing Command Set with other elements is non-conformant so we
        #   require `write_like_original` to be True
        command_set = get_item(dataset, slice(0x00000000, 0x00010000))
        if command_set and write_like_original:
            fp.is_implicit_VR = True
            fp.is_little_endian = True
            write_dataset(fp, command_set)

        # Set file VR and endianness. MUST BE AFTER writing META INFO (which
        #   requires Explicit VR Little Endian) and COMMAND SET (which requires
        #   Implicit VR Little Endian)
        fp.is_implicit_VR = dataset.is_implicit_VR
        fp.is_little_endian = dataset.is_little_endian

        # Write non-Command Set elements now
        write_dataset(fp, get_item(dataset, slice(0x00010000, None)))
    finally:
        if not caller_owns_file:
            fp.close()