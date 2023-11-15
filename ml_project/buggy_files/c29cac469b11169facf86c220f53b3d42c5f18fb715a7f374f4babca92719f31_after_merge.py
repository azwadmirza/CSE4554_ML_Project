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

    # TODO(shoyer): convert everything above to use coders
    var = Variable(dimensions, data, attributes, encoding)

    if mask_and_scale:
        for coder in [variables.UnsignedIntegerCoder(),
                      variables.CFMaskCoder(),
                      variables.CFScaleOffsetCoder()]:
            var = coder.decode(var, name=name)
    if decode_times:
        for coder in [times.CFTimedeltaCoder(),
                      times.CFDatetimeCoder()]:
            var = coder.decode(var, name=name)

    dimensions, data, attributes, encoding = (
        variables.unpack_for_decoding(var))
    # TODO(shoyer): convert everything below to use coders

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