def _write_mseed(stream, filename, encoding=None, reclen=None, byteorder=None,
                 sequence_number=None, flush=True, verbose=0, **_kwargs):
    """
    Write Mini-SEED file from a Stream object.

    .. warning::
        This function should NOT be called directly, it registers via the
        the :meth:`~obspy.core.stream.Stream.write` method of an
        ObsPy :class:`~obspy.core.stream.Stream` object, call this instead.

    :type stream: :class:`~obspy.core.stream.Stream`
    :param stream: A Stream object.
    :type filename: str
    :param filename: Name of the output file or a file-like object.
    :type encoding: int or str, optional
    :param encoding: Should be set to one of the following supported Mini-SEED
        data encoding formats: ``ASCII`` (``0``)*, ``INT16`` (``1``),
        ``INT32`` (``3``), ``FLOAT32`` (``4``)*, ``FLOAT64`` (``5``)*,
        ``STEIM1`` (``10``) and ``STEIM2`` (``11``)*. If no encoding is given
        it will be derived from the dtype of the data and the appropriate
        default encoding (depicted with an asterix) will be chosen.
    :type reclen: int, optional
    :param reclen: Should be set to the desired data record length in bytes
        which must be expressible as 2 raised to the power of X where X is
        between (and including) 8 to 20.
        Defaults to 4096
    :type byteorder: int or str, optional
    :param byteorder: Must be either ``0`` or ``'<'`` for LSBF or
        little-endian, ``1`` or ``'>'`` for MBF or big-endian. ``'='`` is the
        native byte order. If ``-1`` it will be passed directly to libmseed
        which will also default it to big endian. Defaults to big endian.
    :type sequence_number: int, optional
    :param sequence_number: Must be an integer ranging between 1 and 999999.
        Represents the sequence count of the first record of each Trace.
        Defaults to 1.
    :type flush: bool, optional
    :param flush: If ``True``, all data will be packed into records. If
        ``False`` new records will only be created when there is enough data to
        completely fill a record. Be careful with this. If in doubt, choose
        ``True`` which is also the default value.
    :type verbose: int, optional
    :param verbose: Controls verbosity, a value of ``0`` will result in no
        diagnostic output.

    .. note::
        The ``reclen``, ``encoding``, ``byteorder`` and ``sequence_count``
        keyword arguments can be set in the ``stats.mseed`` of
        each :class:`~obspy.core.trace.Trace` as well as ``kwargs`` of this
        function. If both are given the ``kwargs`` will be used.

        The ``stats.mseed.blkt1001.timing_quality`` value will also be written
        if it is set.

        The ``stats.mseed.blkt1001.timing_quality`` value will also be written
        if it is set.

    .. rubric:: Example

    >>> from obspy import read
    >>> st = read()
    >>> st.write('filename.mseed', format='MSEED')  # doctest: +SKIP
    """
    # Map flush and verbose flags.
    if flush:
        flush = 1
    else:
        flush = 0

    if not verbose:
        verbose = 0
    if verbose is True:
        verbose = 1

    # Some sanity checks for the keyword arguments.
    if reclen is not None and reclen not in VALID_RECORD_LENGTHS:
        msg = 'Invalid record length. The record length must be a value\n' + \
            'of 2 to the power of X where 8 <= X <= 20.'
        raise ValueError(msg)
    if byteorder is not None and byteorder not in [0, 1, -1]:
        if byteorder == '=':
            byteorder = NATIVE_BYTEORDER
        # If not elif because NATIVE_BYTEORDER is '<' or '>'.
        if byteorder == '<':
            byteorder = 0
        elif byteorder == '>':
            byteorder = 1
        else:
            msg = "Invalid byte order. It must be either '<', '>', '=', " + \
                  "0, 1 or -1"
            raise ValueError(msg)

    if encoding is not None:
        encoding = util._convert_and_check_encoding_for_writing(encoding)

    if sequence_number is not None:
        # Check sequence number type
        try:
            sequence_number = int(sequence_number)
            # Check sequence number value
            if sequence_number < 1 or sequence_number > 999999:
                raise ValueError("Sequence number out of range. It must be " +
                                 " between 1 and 999999.")
        except (TypeError, ValueError):
            msg = "Invalid sequence number. It must be an integer ranging " +\
                  "from 1 to 999999."
            raise ValueError(msg)

    trace_attributes = []
    use_blkt_1001 = False

    # The data might need to be modified. To not modify the input data keep
    # references of which data to finally write.
    trace_data = []
    # Loop over every trace and figure out the correct settings.
    for _i, trace in enumerate(stream):
        # Create temporary dict for storing information while writing.
        trace_attr = {}
        trace_attributes.append(trace_attr)

        # Figure out whether or not to use Blockette 1001. This check is done
        # once to ensure that Blockette 1001 is either written for every record
        # in the file or for none. It checks the starttime, the sampling rate
        # and the timing quality. If starttime or sampling rate has a precision
        # of more than 100 microseconds, or if timing quality is set, \
        # Blockette 1001 will be written for every record.
        starttime = util._convert_datetime_to_mstime(trace.stats.starttime)
        if starttime % 100 != 0 or \
           (1.0 / trace.stats.sampling_rate * HPTMODULUS) % 100 != 0:
            use_blkt_1001 = True

        if hasattr(trace.stats, 'mseed') and \
           hasattr(trace.stats['mseed'], 'blkt1001') and \
           hasattr(trace.stats['mseed']['blkt1001'], 'timing_quality'):

            timing_quality = trace.stats['mseed']['blkt1001']['timing_quality']
            # Check timing quality type
            try:
                timing_quality = int(timing_quality)
                if timing_quality < 0 or timing_quality > 100:
                    raise ValueError("Timing quality out of range. It must be "
                                     "between 0 and 100.")
            except ValueError:
                msg = "Invalid timing quality in Stream[%i].stats." % _i + \
                    "mseed.timing_quality. It must be an integer ranging" + \
                    " from 0 to 100"
                raise ValueError(msg)

            trace_attr['timing_quality'] = timing_quality
            use_blkt_1001 = True
        else:
            trace_attr['timing_quality'] = timing_quality = 0

        if sequence_number is not None:
            trace_attr['sequence_number'] = sequence_number
        elif hasattr(trace.stats, 'mseed') and \
                hasattr(trace.stats['mseed'], 'sequence_number'):

            sequence_number = trace.stats['mseed']['sequence_number']
            # Check sequence number type
            try:
                sequence_number = int(sequence_number)
                # Check sequence number value
                if sequence_number < 1 or sequence_number > 999999:
                    raise ValueError("Sequence number out of range in " +
                                     "Stream[%i].stats. It must be between " +
                                     "1 and 999999.")
            except (TypeError, ValueError):
                msg = "Invalid sequence number in Stream[%i].stats." % _i +\
                      "mseed.sequence_number. It must be an integer ranging" +\
                      " from 1 to 999999."
                raise ValueError(msg)
            trace_attr['sequence_number'] = sequence_number
        else:
            trace_attr['sequence_number'] = sequence_number = 1

        # Set data quality to indeterminate (= D) if it is not already set.
        try:
            trace_attr['dataquality'] = \
                trace.stats['mseed']['dataquality'].upper()
        except Exception:
            trace_attr['dataquality'] = 'D'
        # Sanity check for the dataquality to get a nice Python exception
        # instead of a C error.
        if trace_attr['dataquality'] not in ['D', 'R', 'Q', 'M']:
            msg = 'Invalid dataquality in Stream[%i].stats' % _i + \
                  '.mseed.dataquality\n' + \
                  'The dataquality for Mini-SEED must be either D, R, Q ' + \
                  'or M. See the SEED manual for further information.'
            raise ValueError(msg)

        # Check that data is of the right type.
        if not isinstance(trace.data, np.ndarray):
            msg = "Unsupported data type %s" % type(trace.data) + \
                  " for Stream[%i].data." % _i
            raise ValueError(msg)

        # Check if ndarray is contiguous (see #192, #193)
        if not trace.data.flags.c_contiguous:
            msg = "Detected non contiguous data array in Stream[%i]" % _i + \
                  ".data. Trying to fix array."
            warnings.warn(msg)
            trace.data = np.ascontiguousarray(trace.data)

        # Handle the record length.
        if reclen is not None:
            trace_attr['reclen'] = reclen
        elif hasattr(trace.stats, 'mseed') and \
                hasattr(trace.stats.mseed, 'record_length'):
            if trace.stats.mseed.record_length in VALID_RECORD_LENGTHS:
                trace_attr['reclen'] = trace.stats.mseed.record_length
            else:
                msg = 'Invalid record length in Stream[%i].stats.' % _i + \
                      'mseed.reclen.\nThe record length must be a value ' + \
                      'of 2 to the power of X where 8 <= X <= 20.'
                raise ValueError(msg)
        else:
            trace_attr['reclen'] = 4096

        # Handle the byte order.
        if byteorder is not None:
            trace_attr['byteorder'] = byteorder
        elif hasattr(trace.stats, 'mseed') and \
                hasattr(trace.stats.mseed, 'byteorder'):
            if trace.stats.mseed.byteorder in [0, 1, -1]:
                trace_attr['byteorder'] = trace.stats.mseed.byteorder
            elif trace.stats.mseed.byteorder == '=':
                if NATIVE_BYTEORDER == '<':
                    trace_attr['byteorder'] = 0
                else:
                    trace_attr['byteorder'] = 1
            elif trace.stats.mseed.byteorder == '<':
                trace_attr['byteorder'] = 0
            elif trace.stats.mseed.byteorder == '>':
                trace_attr['byteorder'] = 1
            else:
                msg = "Invalid byteorder in Stream[%i].stats." % _i + \
                    "mseed.byteorder. It must be either '<', '>', '='," + \
                    " 0, 1 or -1"
                raise ValueError(msg)
        else:
            trace_attr['byteorder'] = 1
        if trace_attr['byteorder'] == -1:
            if NATIVE_BYTEORDER == '<':
                trace_attr['byteorder'] = 0
            else:
                trace_attr['byteorder'] = 1

        # Handle the encoding.
        trace_attr['encoding'] = None
        # If encoding arrives here it is already guaranteed to be a valid
        # integer encoding.
        if encoding is not None:
            # Check if the dtype for all traces is compatible with the enforced
            # encoding.
            ident, _, dtype, _ = ENCODINGS[encoding]
            if trace.data.dtype.type != dtype:
                msg = """
                    Wrong dtype for Stream[%i].data for encoding %s.
                    Please change the dtype of your data or use an appropriate
                    encoding. See the obspy.io.mseed documentation for more
                    information.
                    """ % (_i, ident)
                raise Exception(msg)
            trace_attr['encoding'] = encoding
        elif hasattr(trace.stats, 'mseed') and hasattr(trace.stats.mseed,
                                                       'encoding'):
            trace_attr["encoding"] = \
                util._convert_and_check_encoding_for_writing(
                    trace.stats.mseed.encoding)
            # Check if the encoding matches the data's dtype.
            if trace.data.dtype.type != ENCODINGS[trace_attr['encoding']][2]:
                msg = 'The encoding specified in ' + \
                      'trace.stats.mseed.encoding does not match the ' + \
                      'dtype of the data.\nA suitable encoding will ' + \
                      'be chosen.'
                warnings.warn(msg, UserWarning)
                trace_attr['encoding'] = None
        # automatically detect encoding if no encoding is given.
        if trace_attr['encoding'] is None:
            if trace.data.dtype.type == np.int32:
                trace_attr['encoding'] = 11
            elif trace.data.dtype.type == np.float32:
                trace_attr['encoding'] = 4
            elif trace.data.dtype.type == np.float64:
                trace_attr['encoding'] = 5
            elif trace.data.dtype.type == np.int16:
                trace_attr['encoding'] = 1
            elif trace.data.dtype.type == np.dtype(native_str('|S1')).type:
                trace_attr['encoding'] = 0
            # int64 data not supported; if possible downcast to int32, else
            # create error message. After bumping up to numpy 1.9.0 this check
            # can be replaced by numpy.can_cast()
            elif trace.data.dtype.type == np.int64:
                # check if data can be safely downcast to int32
                ii32 = np.iinfo(np.int32)
                if abs(trace.max()) <= ii32.max:
                    trace_data.append(_np_copy_astype(trace.data, np.int32))
                    trace_attr['encoding'] = 11
                else:
                    msg = ("int64 data only supported when writing MSEED if "
                           "it can be downcast to int32 type data.")
                    raise ObsPyMSEEDError(msg)
            else:
                msg = "Unsupported data type %s in Stream[%i].data" % \
                    (trace.data.dtype, _i)
                raise Exception(msg)

        # Convert data if necessary, otherwise store references in list.
        if trace_attr['encoding'] == 1:
            # INT16 needs INT32 data type
            trace_data.append(_np_copy_astype(trace.data, np.int32))
        else:
            trace_data.append(trace.data)

    # Do some final sanity checks and raise a warning if a file will be written
    # with more than one different encoding, record length or byte order.
    encodings = {_i['encoding'] for _i in trace_attributes}
    reclens = {_i['reclen'] for _i in trace_attributes}
    byteorders = {_i['byteorder'] for _i in trace_attributes}
    msg = 'File will be written with more than one different %s.\n' + \
          'This might have a negative influence on the compatibility ' + \
          'with other programs.'
    if len(encodings) != 1:
        warnings.warn(msg % 'encodings')
    if len(reclens) != 1:
        warnings.warn(msg % 'record lengths')
    if len(byteorders) != 1:
        warnings.warn(msg % 'byteorders')

    # Open filehandler or use an existing file like object.
    if not hasattr(filename, 'write'):
        f = open(filename, 'wb')
    else:
        f = filename

    # Loop over every trace and finally write it to the filehandler.
    for trace, data, trace_attr in zip(stream, trace_data, trace_attributes):
        if not len(data):
            msg = 'Skipping empty trace "%s".' % (trace)
            warnings.warn(msg)
            continue
        # Create C struct MSTrace.
        mst = MST(trace, data, dataquality=trace_attr['dataquality'])

        # Initialize packedsamples pointer for the mst_pack function
        packedsamples = C.c_int()

        # Callback function for mst_pack to actually write the file
        def record_handler(record, reclen, _stream):
            f.write(record[0:reclen])
        # Define Python callback function for use in C function
        rec_handler = C.CFUNCTYPE(C.c_void_p, C.POINTER(C.c_char), C.c_int,
                                  C.c_void_p)(record_handler)

        # Fill up msr record structure, this is already contained in
        # mstg, however if blk1001 is set we need it anyway
        msr = clibmseed.msr_init(None)
        msr.contents.network = trace.stats.network.encode('ascii', 'strict')
        msr.contents.station = trace.stats.station.encode('ascii', 'strict')
        msr.contents.location = trace.stats.location.encode('ascii', 'strict')
        msr.contents.channel = trace.stats.channel.encode('ascii', 'strict')
        msr.contents.dataquality = trace_attr['dataquality'].\
            encode('ascii', 'strict')

        # Set starting sequence number
        msr.contents.sequence_number = trace_attr['sequence_number']

        # Only use Blockette 1001 if necessary.
        if use_blkt_1001:
            # Timing quality has been set in trace_attr

            size = C.sizeof(Blkt1001S)
            # Only timing quality matters here, other blockette attributes will
            # be filled by libmseed.msr_normalize_header
            blkt_value = pack(native_str("BBBB"), trace_attr['timing_quality'],
                              0, 0, 0)
            blkt_ptr = C.create_string_buffer(blkt_value, len(blkt_value))

            # Usually returns a pointer to the added blockette in the
            # blockette link chain and a NULL pointer if it fails.
            # NULL pointers have a false boolean value according to the
            # ctypes manual.
            ret_val = clibmseed.msr_addblockette(msr, blkt_ptr,
                                                 size, 1001, 0)

            if bool(ret_val) is False:
                clibmseed.msr_free(C.pointer(msr))
                del msr
                raise Exception('Error in msr_addblockette')

        # Only use Blockette 100 if necessary.
        # Determine if a blockette 100 will be needed to represent the input
        # sample rate or if the sample rate in the fixed section of the data
        # header will suffice (see ms_genfactmult in libmseed/genutils.c)
        use_blkt_100 = False

        _factor = C.c_int16()
        _multiplier = C.c_int16()
        _retval = clibmseed.ms_genfactmult(
            trace.stats.sampling_rate, C.pointer(_factor),
            C.pointer(_multiplier))
        # Use blockette 100 if ms_genfactmult() failed.
        if _retval != 0:
            use_blkt_100 = True
        # Otherwise figure out if ms_genfactmult() found exact factors.
        # Otherwise write blockette 100.
        else:
            ms_sr = clibmseed.ms_nomsamprate(_factor.value, _multiplier.value)

            # It is also necessary if the libmseed calculated sampling rate
            # would result in a loss of accuracy - the floating point
            # comparision is on purpose here as it will always try to
            # preserve all accuracy.
            # Cast to float32 to not add blockette 100 for values
            # that cannot be represented with 32bits.
            if np.float32(ms_sr) != np.float32(trace.stats.sampling_rate):
                use_blkt_100 = True

        if use_blkt_100:
            size = C.sizeof(Blkt100S)
            blkt100 = C.c_char(b' ')
            C.memset(C.pointer(blkt100), 0, size)
            ret_val = clibmseed.msr_addblockette(
                msr, C.pointer(blkt100), size, 100, 0)  # NOQA
            # Usually returns a pointer to the added blockette in the
            # blockette link chain and a NULL pointer if it fails.
            # NULL pointers have a false boolean value according to the
            # ctypes manual.
            if bool(ret_val) is False:
                clibmseed.msr_free(C.pointer(msr))  # NOQA
                del msr  # NOQA
                raise Exception('Error in msr_addblockette')

        # Pack mstg into a MSEED file using the callback record_handler as
        # write method.
        errcode = clibmseed.mst_pack(
            mst.mst, rec_handler, None, trace_attr['reclen'],
            trace_attr['encoding'], trace_attr['byteorder'],
            C.byref(packedsamples), flush, verbose, msr)  # NOQA

        if errcode == 0:
            msg = ("Did not write any data for trace '%s' even though it "
                   "contains data values.") % trace
            raise ValueError(msg)
        if errcode == -1:
            clibmseed.msr_free(C.pointer(msr))  # NOQA
            del mst, msr  # NOQA
            raise Exception('Error in mst_pack')
        # Deallocate any allocated memory.
        clibmseed.msr_free(C.pointer(msr))  # NOQA
        del mst, msr  # NOQA
    # Close if its a file handler.
    if not hasattr(filename, 'write'):
        f.close()