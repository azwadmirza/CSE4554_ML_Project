def empty_value_for_VR(VR, raw=False):
    """Return the value for an empty element for `VR`.

    The behavior of this property depends on the setting of
    :attr:`config.use_none_as_empty_value`. If that is set to ``True``,
    an empty value is represented by ``None`` (except for VR 'SQ'), otherwise
    it depends on `VR`. For text VRs (this includes 'AE', 'AS', 'CS', 'DA',
    'DT', 'LO', 'LT', 'PN', 'SH', 'ST', 'TM', 'UC', 'UI', 'UR' and 'UT') an
    empty string is used as empty value representation, for all other VRs
    except 'SQ', ``None``. For empty sequence values (VR 'SQ') an empty list
    is used in all cases.
    Note that this is used only if decoding the element - it is always
    possible to set the value to another empty value representation,
    which will be preserved during the element object lifetime.

    Parameters
    ----------
    VR : str
        The VR of the corresponding element.

    raw : bool
        If ``True``, returns the value for a :class:`RawDataElement`,
        otherwise for a :class:`DataElement`

    Returns
    -------
    str or bytes or None or list
        The value a data element with `VR` is assigned on decoding
        if it is empty.
    """
    if VR == 'SQ':
        return []
    if config.use_none_as_empty_text_VR_value:
        return None
    if VR in ('AE', 'AS', 'CS', 'DA', 'DT', 'LO', 'LT',
              'PN', 'SH', 'ST', 'TM', 'UC', 'UI', 'UR', 'UT'):
        return b'' if raw else ''
    return None