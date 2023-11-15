def decode_cf_variable(name, var, concat_characters=True, mask_and_scale=True,
                       decode_times=True, decode_endianness=True,
                       stack_char_dim=True):
    """
    Decodes a variable which may hold CF encoded information.

    This includes variables that have been masked and scaled, which
    hold CF style time variables (this is almost always the case if
    the dataset has been serialized) and which have strings encoded
    as character arrays.

    Parameters
    ----------
    name: str
        Name of the variable. Used for better error messages.
    var : Variable
        A variable holding potentially CF encoded information.
    concat_characters : bool
        Should character arrays be concatenated to strings, for
        example: ['h', 'e', 'l', 'l', 'o'] -> 'hello'
    mask_and_scale: bool
        Lazily scale (using scale_factor and add_offset) and mask
        (using _FillValue). If the _Unsigned attribute is present
        treat integer arrays as unsigned.
    decode_times : bool
        Decode cf times ('hours since 2000-01-01') to np.datetime64.
    decode_endianness : bool
        Decode arrays from non-native to native endianness.
    stack_char_dim : bool
        Whether to stack characters into bytes along the last dimension of this
        array. Passed as an argument because we need to look at the full
        dataset to figure out if this is appropriate.

    Returns
    -------
    out : Variable
        A variable holding the decoded equivalent of var.
    """
    # use _data instead of data so as not to trigger loading data
    var = as_variable(var)
    data = var._data
    dimensions = var.dims
    attributes = var.attrs.copy()
    encoding = var.encoding.copy()

    original_dtype = data.dtype

    if concat_characters and data.dtype.kind == 'S':
        if stack_char_dim:
            dimensions = dimensions[:-1]
            data = StackedBytesArray(data)

        string_encoding = pop_to(attributes, encoding, '_Encoding')
        if string_encoding is not None:
            data = BytesToStringArray(data, string_encoding)

    unsigned = pop_to(attributes, encoding, '_Unsigned')
    if unsigned and mask_and_scale:
        if data.dtype.kind == 'i':
            data = UnsignedIntTypeArray(data)
        else:
            warnings.warn("variable %r has _Unsigned attribute but is not "
                          "of integer type. Ignoring attribute." % name,
                          SerializationWarning, stacklevel=3)

    if mask_and_scale:
        if 'missing_value' in attributes:
            # missing_value is deprecated, but we still want to support it as
            # an alias for _FillValue.
            if ('_FillValue' in attributes and
                not utils.equivalent(attributes['_FillValue'],
                                     attributes['missing_value'])):
                raise ValueError("Conflicting _FillValue and missing_value "
                                 "attributes on a variable {!r}: {} vs. {}\n\n"
                                 "Consider opening the offending dataset "
                                 "using decode_cf=False, correcting the "
                                 "attributes and decoding explicitly using "
                                 "xarray.decode_cf()."
                                 .format(name, attributes['_FillValue'],
                                         attributes['missing_value']))
            attributes['_FillValue'] = attributes.pop('missing_value')

        fill_value = pop_to(attributes, encoding, '_FillValue')
        if isinstance(fill_value, np.ndarray) and fill_value.size > 1:
            warnings.warn("variable {!r} has multiple fill values {}, "
                          "decoding all values to NaN."
                          .format(name, fill_value),
                          SerializationWarning, stacklevel=3)

        scale_factor = pop_to(attributes, encoding, 'scale_factor')
        add_offset = pop_to(attributes, encoding, 'add_offset')
        has_fill = (fill_value is not None and
                    not np.any(pd.isnull(fill_value)))
        if (has_fill or scale_factor is not None or add_offset is not None):
            if has_fill and np.array(fill_value).dtype.kind in ['U', 'S', 'O']:
                if string_encoding is not None:
                    raise NotImplementedError(
                        'variable %r has a _FillValue specified, but '
                        '_FillValue is yet supported on unicode strings: '
                        'https://github.com/pydata/xarray/issues/1647')
                dtype = object
            else:
                # According to the CF spec, the fill value is of the same
                # type as its variable, i.e. its storage format on disk.
                # This handles the case where the fill_value also needs to be
                # converted to its unsigned value.
                if has_fill:
                    fill_value = data.dtype.type(fill_value)
                dtype = float

            data = MaskedAndScaledArray(data, fill_value, scale_factor,
                                        add_offset, dtype)

    if decode_times and 'units' in attributes:
        if 'since' in attributes['units']:
            # datetime
            units = pop_to(attributes, encoding, 'units')
            calendar = pop_to(attributes, encoding, 'calendar')
            data = DecodedCFDatetimeArray(data, units, calendar)
        elif attributes['units'] in TIME_UNITS:
            # timedelta
            units = pop_to(attributes, encoding, 'units')
            data = DecodedCFTimedeltaArray(data, units)

    if decode_endianness and not data.dtype.isnative:
        # do this last, so it's only done if we didn't already unmask/scale
        data = NativeEndiannessArray(data)
        original_dtype = data.dtype

    if 'dtype' in encoding:
        if original_dtype != encoding['dtype']:
            warnings.warn("CF decoding is overwriting dtype on variable {!r}"
                          .format(name))
    else:
        encoding['dtype'] = original_dtype

    if 'dtype' in attributes and attributes['dtype'] == 'bool':
        del attributes['dtype']
        data = BoolTypeArray(data)

    return Variable(dimensions, indexing.LazilyIndexedArray(data),
                    attributes, encoding=encoding)