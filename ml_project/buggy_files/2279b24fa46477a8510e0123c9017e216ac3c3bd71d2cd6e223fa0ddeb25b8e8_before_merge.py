def read_partial(fileobj, stop_when=None, defer_size=None,
                 force=False, specific_tags=None):
    """Parse a DICOM file until a condition is met.

    Parameters
    ----------
    fileobj : a file-like object
        Note that the file will not close when the function returns.
    stop_when :
        Stop condition. See ``read_dataset`` for more info.
    defer_size : int, str, None, optional
        See ``dcmread`` for parameter info.
    force : boolean
        See ``dcmread`` for parameter info.
    specific_tags : list or None
        See ``dcmread`` for parameter info.

    Notes
    -----
    Use ``dcmread`` unless you need to stop on some condition other than
    reaching pixel data.

    Returns
    -------
    FileDataset instance or DicomDir instance.

    See Also
    --------
    dcmread
        More generic file reading function.
    """
    # Read File Meta Information

    # Read preamble (if present)
    preamble = read_preamble(fileobj, force)
    # Read any File Meta Information group (0002,eeee) elements (if present)
    file_meta_dataset = _read_file_meta_info(fileobj)

    # Read Dataset

    # Read any Command Set group (0000,eeee) elements (if present)
    command_set = _read_command_set_elements(fileobj)

    # Check to see if there's anything left to read
    peek = fileobj.read(1)
    fileobj.seek(-1, 1)

    # `filobj` should be positioned at the start of the dataset by this point.
    # Ensure we have appropriate values for `is_implicit_VR` and
    # `is_little_endian` before we try decoding. We assume an initial
    # transfer syntax of implicit VR little endian and correct it as necessary
    is_implicit_VR = True
    is_little_endian = True
    transfer_syntax = file_meta_dataset.get("TransferSyntaxUID")
    if peek == b'':  # EOF
        pass
    elif transfer_syntax is None:  # issue 258
        # If no TransferSyntaxUID element then we have to try and figure out
        #   the correct values for `is_little_endian` and `is_implicit_VR`.
        # Peek at the first 6 bytes to get the first element's tag group and
        #   (possibly) VR
        group, _, VR = unpack("<HH2s", fileobj.read(6))
        fileobj.seek(-6, 1)

        # Test the VR to see if it's valid, and if so then assume explicit VR
        from pydicom.values import converters
        if not in_py2:
            VR = VR.decode(default_encoding)
        if VR in converters.keys():
            is_implicit_VR = False
            # Big endian encoding can only be explicit VR
            #   Big endian 0x0004 decoded as little endian will be 1024
            #   Big endian 0x0100 decoded as little endian will be 1
            # Therefore works for big endian tag groups up to 0x00FF after
            #   which it will fail, in which case we leave it as little endian
            #   and hope for the best (big endian is retired anyway)
            if group >= 1024:
                is_little_endian = False
    elif transfer_syntax == pydicom.uid.ImplicitVRLittleEndian:
        pass
    elif transfer_syntax == pydicom.uid.ExplicitVRLittleEndian:
        is_implicit_VR = False
    elif transfer_syntax == pydicom.uid.ExplicitVRBigEndian:
        is_implicit_VR = False
        is_little_endian = False
    elif transfer_syntax == pydicom.uid.DeflatedExplicitVRLittleEndian:
        # See PS3.6-2008 A.5 (p 71)
        # when written, the entire dataset following
        #     the file metadata was prepared the normal way,
        #     then "deflate" compression applied.
        #  All that is needed here is to decompress and then
        #     use as normal in a file-like object
        zipped = fileobj.read()
        # -MAX_WBITS part is from comp.lang.python answer:
        # groups.google.com/group/comp.lang.python/msg/e95b3b38a71e6799
        unzipped = zlib.decompress(zipped, -zlib.MAX_WBITS)
        fileobj = BytesIO(unzipped)  # a file-like object
        is_implicit_VR = False
    else:
        # Any other syntax should be Explicit VR Little Endian,
        #   e.g. all Encapsulated (JPEG etc) are ExplVR-LE
        #        by Standard PS 3.5-2008 A.4 (p63)
        is_implicit_VR = False

    # Try and decode the dataset
    #   By this point we should be at the start of the dataset and have
    #   the transfer syntax (whether read from the file meta or guessed at)
    try:
        dataset = read_dataset(fileobj, is_implicit_VR, is_little_endian,
                               stop_when=stop_when, defer_size=defer_size,
                               specific_tags=specific_tags)
    except EOFError:
        pass  # error already logged in read_dataset

    # Add the command set elements to the dataset (if any)
    dataset.update(command_set.tags)

    class_uid = file_meta_dataset.get("MediaStorageSOPClassUID", None)
    if class_uid and class_uid.name == "Media Storage Directory Storage":
        dataset_class = DicomDir
    else:
        dataset_class = FileDataset
    new_dataset = dataset_class(fileobj, dataset, preamble, file_meta_dataset,
                                is_implicit_VR, is_little_endian)
    # save the originally read transfer syntax properties in the dataset
    new_dataset.set_original_encoding(is_implicit_VR, is_little_endian,
                                      dataset._character_set)
    return new_dataset