def _read_file_meta_info(fp):
    """Return a Dataset containing any File Meta (0002,eeee) elements in `fp`.

    File Meta elements are always Explicit VR Little Endian (as per PS3.10
    Section 7). Once any File Meta elements are read `fp` will be positioned
    at the start of the next group of elements.

    Parameters
    ----------
    fp : file-like
        The file-like positioned at the start of any File Meta Information
        group elements.

    Returns
    -------
    pydicom.dataset.Dataset
        The File Meta elements as a Dataset instance. May be empty if no
        File Meta are present.
    """

    def _not_group_0002(tag, VR, length):
        """Return True if the tag is not in group 0x0002, False otherwise."""
        return tag.group != 2

    start_file_meta = fp.tell()
    file_meta = read_dataset(fp, is_implicit_VR=False, is_little_endian=True,
                             stop_when=_not_group_0002)
    if not file_meta._dict:
        return file_meta

    # Test the file meta for correct interpretation by requesting the first
    #   data element: if it fails, retry loading the file meta with an
    #   implicit VR (issue #503)
    try:
        file_meta[list(file_meta.elements())[0].tag]
    except NotImplementedError:
        fp.seek(start_file_meta)
        file_meta = read_dataset(fp, is_implicit_VR=True,
                                 is_little_endian=True,
                                 stop_when=_not_group_0002)

    # Log if the Group Length doesn't match actual length
    if 'FileMetaInformationGroupLength' in file_meta:
        # FileMetaInformationGroupLength must be 12 bytes long and its value
        #   counts from the beginning of the next element to the end of the
        #   file meta elements
        length_file_meta = fp.tell() - (start_file_meta + 12)
        if file_meta.FileMetaInformationGroupLength != length_file_meta:
            logger.info("_read_file_meta_info: (0002,0000) 'File Meta "
                        "Information Group Length' value doesn't match the "
                        "actual File Meta Information length ({0} vs {1} "
                        "bytes)."
                        .format(file_meta.FileMetaInformationGroupLength,
                                length_file_meta))

    return file_meta