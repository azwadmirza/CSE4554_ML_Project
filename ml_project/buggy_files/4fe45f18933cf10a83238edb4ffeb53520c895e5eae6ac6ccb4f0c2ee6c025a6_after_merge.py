def DataElement_from_raw(raw_data_element, encoding=None):
    """Return a :class:`DataElement` created from `raw_data_element`.

    Parameters
    ----------
    raw_data_element : RawDataElement namedtuple
        The raw data to convert to a :class:`DataElement`.
    encoding : str, optional
        The character encoding of the raw data.

    Returns
    -------
    DataElement
    """
    # XXX buried here to avoid circular import
    # filereader->Dataset->convert_value->filereader
    # (for SQ parsing)

    if in_py2:
        encoding = encoding or default_encoding
    from pydicom.values import convert_value
    raw = raw_data_element

    # If user has hooked into conversion of raw values, call his/her routine
    if config.data_element_callback:
        data_elem = config.data_element_callback
        raw = data_elem(raw_data_element,
                        **config.data_element_callback_kwargs)
    VR = raw.VR
    if VR is None:  # Can be if was implicit VR
        try:
            VR = dictionary_VR(raw.tag)
        except KeyError:
            # just read the bytes, no way to know what they mean
            if raw.tag.is_private:
                # for VR for private tags see PS3.5, 6.2.2
                if raw.tag.is_private_creator:
                    VR = 'LO'
                else:
                    VR = 'UN'

            # group length tag implied in versions < 3.0
            elif raw.tag.element == 0:
                VR = 'UL'
            else:
                msg = "Unknown DICOM tag {0:s}".format(str(raw.tag))
                msg += " can't look up VR"
                raise KeyError(msg)
    elif VR == 'UN' and not raw.tag.is_private:
        # handle rare case of incorrectly set 'UN' in explicit encoding
        # see also DataElement.__init__()
        if (raw.length == 0xffffffff or raw.value is None or
                len(raw.value) < 0xffff):
            try:
                VR = dictionary_VR(raw.tag)
            except KeyError:
                pass
    try:
        value = convert_value(VR, raw, encoding)
    except NotImplementedError as e:
        raise NotImplementedError("{0:s} in tag {1!r}".format(str(e), raw.tag))

    if raw.tag in _LUT_DESCRIPTOR_TAGS and value[0] < 0:
        # We only fix the first value as the third value is 8 or 16
        value[0] += 65536

    return DataElement(raw.tag, VR, value, raw.value_tell,
                       raw.length == 0xFFFFFFFF, already_converted=True)