def _get_record_information(file_object, offset=0, endian=None):
    """
    Searches the first MiniSEED record stored in file_object at the current
    position and returns some information about it.

    If offset is given, the MiniSEED record is assumed to start at current
    position + offset in file_object.

    :param endian: If given, the byte order will be enforced. Can be either "<"
        or ">". If None, it will be determined automatically.
        Defaults to None.
    """
    initial_position = file_object.tell()
    record_start = initial_position
    samp_rate = None

    info = {}

    # Apply the offset.
    if offset:
        file_object.seek(offset, 1)
        record_start += offset

    # Get the size of the buffer.
    file_object.seek(0, 2)
    info['filesize'] = int(file_object.tell() - record_start)
    file_object.seek(record_start, 0)

    _code = file_object.read(8)[6:7]
    # Reset the offset if starting somewhere in the middle of the file.
    if info['filesize'] % 128 != 0:
        # if a multiple of minimal record length 256
        record_start = 0
    elif _code not in [b'D', b'R', b'Q', b'M', b' ']:
        # if valid data record start at all starting with D, R, Q or M
        record_start = 0
    # Might be a noise record or completely empty.
    elif _code == b' ':
        try:
            _t = file_object.read(120).decode().strip()
        except Exception:
            raise ValueError("Invalid MiniSEED file.")
        if not _t:
            info = _get_record_information(file_object=file_object,
                                           endian=endian)
            file_object.seek(initial_position, 0)
            return info
        else:
            raise ValueError("Invalid MiniSEED file.")
    file_object.seek(record_start, 0)

    # check if full SEED or MiniSEED
    if file_object.read(8)[6:7] == b'V':
        # found a full SEED record - seek first MiniSEED record
        # search blockette 005, 008 or 010 which contain the record length
        blockette_id = file_object.read(3)
        while blockette_id not in [b'010', b'008', b'005']:
            if not blockette_id.startswith(b'0'):
                msg = "SEED Volume Index Control Headers: blockette 0xx" + \
                      " expected, got %s"
                raise Exception(msg % blockette_id)
            # get length and jump to end of current blockette
            blockette_len = int(file_object.read(4))
            file_object.seek(blockette_len - 7, 1)
            # read next blockette id
            blockette_id = file_object.read(3)
        # Skip the next bytes containing length of the blockette and version
        file_object.seek(8, 1)
        # get record length
        rec_len = pow(2, int(file_object.read(2)))
        # reset file pointer
        file_object.seek(record_start, 0)
        # cycle through file using record length until first data record found
        while file_object.read(7)[6:7] not in [b'D', b'R', b'Q', b'M']:
            record_start += rec_len
            file_object.seek(record_start, 0)

    # Jump to the network, station, location and channel codes.
    file_object.seek(record_start + 8, 0)
    data = file_object.read(12)

    info["station"] = _decode_header_field("station", data[:5].strip())
    info["location"] = _decode_header_field("location", data[5:7].strip())
    info["channel"] = _decode_header_field("channel", data[7:10].strip())
    info["network"] = _decode_header_field("network", data[10:12].strip())

    # Use the date to figure out the byte order.
    file_object.seek(record_start + 20, 0)
    # Capital letters indicate unsigned quantities.
    data = file_object.read(28)

    def fmt(s):
        return native_str('%sHHBBBxHHhhBBBxlxxH' % s)

    def _parse_time(values):
        if not (1 <= values[1] <= 366):
            msg = 'julday out of bounds (wrong endian?): {!s}'.format(
                values[1])
            raise InternalMSEEDParseTimeError(msg)
        # The spec says values[5] (.0001 seconds) must be between 0-9999 but
        # we've  encountered files which have a value of 10000. We interpret
        # this as an additional second. The approach here is general enough
        # to work for any value of values[5].
        msec = values[5] * 100
        offset = msec // 1000000
        if offset:
            warnings.warn(
                "Record contains a fractional seconds (.0001 secs) of %i - "
                "the maximum strictly allowed value is 9999. It will be "
                "interpreted as one or more additional seconds." % values[5],
                category=UserWarning)
        try:
            t = UTCDateTime(
                year=values[0], julday=values[1],
                hour=values[2], minute=values[3], second=values[4],
                microsecond=msec % 1000000) + offset
        except TypeError:
            msg = 'Problem decoding time (wrong endian?)'
            raise InternalMSEEDParseTimeError(msg)
        return t

    if endian is None:
        try:
            endian = ">"
            values = unpack(fmt(endian), data)
            starttime = _parse_time(values)
        except InternalMSEEDParseTimeError:
            endian = "<"
            values = unpack(fmt(endian), data)
            starttime = _parse_time(values)
    else:
        values = unpack(fmt(endian), data)
        try:
            starttime = _parse_time(values)
        except InternalMSEEDParseTimeError:
            msg = ("Invalid starttime found. The passed byte order is likely "
                   "wrong.")
            raise ValueError(msg)
    npts = values[6]
    info['npts'] = npts
    samp_rate_factor = values[7]
    samp_rate_mult = values[8]
    info['activity_flags'] = values[9]
    # Bit 1 of the activity flags.
    time_correction_applied = bool(info['activity_flags'] & 2)
    info['io_and_clock_flags'] = values[10]
    info['data_quality_flags'] = values[11]
    info['time_correction'] = values[12]
    time_correction = values[12]
    blkt_offset = values[13]

    # Correct the starttime if applicable.
    if (time_correction_applied is False) and time_correction:
        # Time correction is in units of 0.0001 seconds.
        starttime += time_correction * 0.0001

    # Traverse the blockettes and parse Blockettes 100, 500, 1000 and/or 1001
    # if any of those is found.
    while blkt_offset:
        file_object.seek(record_start + blkt_offset, 0)
        blkt_type, next_blkt = unpack(native_str('%sHH' % endian),
                                      file_object.read(4))
        if next_blkt != 0 and (next_blkt < 4 or next_blkt - 4 <= blkt_offset):
            msg = ('Invalid blockette offset (%d) less than or equal to '
                   'current offset (%d)') % (next_blkt, blkt_offset)
            raise ValueError(msg)
        blkt_offset = next_blkt

        # Parse in order of likeliness.
        if blkt_type == 1000:
            encoding, word_order, record_length = \
                unpack(native_str('%sBBB' % endian),
                       file_object.read(3))
            if word_order not in ENDIAN:
                msg = ('Invalid word order "%s" in blockette 1000 for '
                       'record with ID %s.%s.%s.%s at offset %i.') % (
                    str(word_order), info["network"], info["station"],
                    info["location"], info["channel"], offset)
                warnings.warn(msg, UserWarning)
            elif ENDIAN[word_order] != endian:
                msg = 'Inconsistent word order.'
                warnings.warn(msg, UserWarning)
            info['encoding'] = encoding
            info['record_length'] = 2 ** record_length
        elif blkt_type == 1001:
            info['timing_quality'], mu_sec = \
                unpack(native_str('%sBb' % endian),
                       file_object.read(2))
            starttime += float(mu_sec) / 1E6
        elif blkt_type == 500:
            file_object.seek(14, 1)
            mu_sec = unpack(native_str('%sb' % endian),
                            file_object.read(1))[0]
            starttime += float(mu_sec) / 1E6
        elif blkt_type == 100:
            samp_rate = unpack(native_str('%sf' % endian),
                               file_object.read(4))[0]

    # No blockette 1000 found.
    if "record_length" not in info:
        file_object.seek(record_start, 0)
        # Read 16 kb - should be a safe maximal record length.
        buf = from_buffer(file_object.read(2 ** 14), dtype=np.int8)
        # This is a messy check - we just delegate to libmseed.
        reclen = clibmseed.ms_detect(buf, len(buf))
        if reclen < 0:
            raise ValueError("Could not detect data record.")
        elif reclen == 0:
            # It might be at the end of the file.
            if len(buf) in [2 ** _i for _i in range(7, 256)]:
                reclen = len(buf)
            else:
                raise ValueError("Could not determine record length.")
        info["record_length"] = reclen

    # If samprate not set via blockette 100 calculate the sample rate according
    # to the SEED manual.
    if not samp_rate:
        if (samp_rate_factor > 0) and (samp_rate_mult) > 0:
            samp_rate = float(samp_rate_factor * samp_rate_mult)
        elif (samp_rate_factor > 0) and (samp_rate_mult) < 0:
            samp_rate = -1.0 * float(samp_rate_factor) / float(samp_rate_mult)
        elif (samp_rate_factor < 0) and (samp_rate_mult) > 0:
            samp_rate = -1.0 * float(samp_rate_mult) / float(samp_rate_factor)
        elif (samp_rate_factor < 0) and (samp_rate_mult) < 0:
            samp_rate = 1.0 / float(samp_rate_factor * samp_rate_mult)
        else:
            samp_rate = 0

    info['samp_rate'] = samp_rate

    info['starttime'] = starttime
    # If sample rate is zero set endtime to startime
    if samp_rate == 0:
        info['endtime'] = starttime
    # Endtime is the time of the last sample.
    else:
        info['endtime'] = starttime + (npts - 1) / samp_rate
    info['byteorder'] = endian

    info['number_of_records'] = int(info['filesize'] //
                                    info['record_length'])
    info['excess_bytes'] = int(info['filesize'] % info['record_length'])

    # Reset file pointer.
    file_object.seek(initial_position, 0)
    return info