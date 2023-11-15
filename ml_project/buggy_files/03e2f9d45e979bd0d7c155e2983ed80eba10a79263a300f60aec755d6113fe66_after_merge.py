def _field_gen(filename, read_data_bytes, little_ended=False):
    """
    Returns a generator of "half-formed" PPField instances derived from
    the given filename.

    A field returned by the generator is only "half-formed" because its
    `_data` attribute represents a simple one-dimensional stream of
    bytes. (Encoded either as an instance of LoadedArrayBytes or as a
    'deferred array bytes' tuple, depending on the value of `read_data_bytes`.)
    This is because fields encoded with a land/sea mask do not contain
    sufficient information within the field to determine the final
    two-dimensional shape of the data.

    The callers of this routine are the 'load' routines (both PP and FF).
    They both filter the resulting stream of fields with `_interpret_fields`,
    which replaces each field.data with an actual array (real or lazy).
    This is done separately so that `_interpret_fields` can detect land-mask
    fields and use them to construct data arrays for any fields which use
    land/sea-mask packing.

    """
    dtype_endian_char = '<' if little_ended else '>'
    with open(filename, 'rb') as pp_file:
        # Get a reference to the seek method on the file
        # (this is accessed 3* #number of headers so can provide a small
        # performance boost)
        pp_file_seek = pp_file.seek
        pp_file_read = pp_file.read

        field_count = 0
        # Keep reading until we reach the end of file
        while True:
            # Move past the leading header length word
            pp_file_seek(PP_WORD_DEPTH, os.SEEK_CUR)
            # Get the LONG header entries
            dtype = '%ci%d' % (dtype_endian_char, PP_WORD_DEPTH)
            header_longs = np.fromfile(pp_file, dtype=dtype,
                                       count=NUM_LONG_HEADERS)
            # Nothing returned => EOF
            if len(header_longs) == 0:
                break
            # Get the FLOAT header entries
            dtype = '%cf%d' % (dtype_endian_char, PP_WORD_DEPTH)
            header_floats = np.fromfile(pp_file, dtype=dtype,
                                        count=NUM_FLOAT_HEADERS)
            header = tuple(header_longs) + tuple(header_floats)

            # Make a PPField of the appropriate sub-class (depends on header
            # release number)
            try:
                pp_field = make_pp_field(header)
            except ValueError as e:
                msg = 'Unable to interpret field {}. {}. Skipping ' \
                      'the remainder of the file.'.format(field_count,
                                                          str(e))
                warnings.warn(msg)
                break

            # Skip the trailing 4-byte word containing the header length
            pp_file_seek(PP_WORD_DEPTH, os.SEEK_CUR)

            # Read the word telling me how long the data + extra data is
            # This value is # of bytes
            len_of_data_plus_extra = struct.unpack_from(
                '%cL' % dtype_endian_char,
                pp_file_read(PP_WORD_DEPTH))[0]
            if len_of_data_plus_extra != pp_field.lblrec * PP_WORD_DEPTH:
                wmsg = ('LBLREC has a different value to the integer recorded '
                        'after the header in the file ({} and {}). '
                        'Skipping the remainder of the file.')
                warnings.warn(wmsg.format(pp_field.lblrec * PP_WORD_DEPTH,
                                          len_of_data_plus_extra))
                break

            # calculate the extra length in bytes
            extra_len = pp_field.lbext * PP_WORD_DEPTH

            # Derive size and datatype of payload
            data_len = len_of_data_plus_extra - extra_len
            dtype = LBUSER_DTYPE_LOOKUP.get(pp_field.lbuser[0],
                                            LBUSER_DTYPE_LOOKUP['default'])
            if little_ended:
                # Change data dtype for a little-ended file.
                dtype = str(dtype)
                if dtype[0] != '>':
                    msg = ("Unexpected dtype {!r} can't be converted to "
                           "little-endian")
                    raise ValueError(msg)

                dtype = np.dtype('<' + dtype[1:])

            if read_data_bytes:
                # Read the actual bytes. This can then be converted to a numpy
                # array at a higher level.
                pp_field.data = LoadedArrayBytes(pp_file.read(data_len),
                                                 dtype)
            else:
                # Provide enough context to read the data bytes later on,
                # as a 'deferred array bytes' tuple.
                # N.B. this used to be a namedtuple called DeferredArrayBytes,
                # but it no longer is. Possibly for performance reasons?
                pp_field.data = (filename, pp_file.tell(), data_len, dtype)
                # Seek over the actual data payload.
                pp_file_seek(data_len, os.SEEK_CUR)

            # Do we have any extra data to deal with?
            if extra_len:
                pp_field._read_extra_data(pp_file, pp_file_read, extra_len,
                                          little_ended=little_ended)

            # Skip that last 4 byte record telling me the length of the field I
            # have already read
            pp_file_seek(PP_WORD_DEPTH, os.SEEK_CUR)
            field_count += 1
            yield pp_field