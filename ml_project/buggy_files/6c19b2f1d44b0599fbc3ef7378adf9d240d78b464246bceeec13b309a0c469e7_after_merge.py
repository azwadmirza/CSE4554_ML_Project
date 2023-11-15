def loadtxt(fname, dtype=float, comments='#', delimiter=None,
            converters=None, skiprows=0, usecols=None, unpack=False,
            ndmin=0):
    """
    Load data from a text file.

    Each row in the text file must have the same number of values.

    Parameters
    ----------
    fname : file or str
        File, filename, or generator to read.  If the filename extension is
        ``.gz`` or ``.bz2``, the file is first decompressed. Note that
        generators should return byte strings for Python 3k.
    dtype : data-type, optional
        Data-type of the resulting array; default: float.  If this is a
        record data-type, the resulting array will be 1-dimensional, and
        each row will be interpreted as an element of the array.  In this
        case, the number of columns used must match the number of fields in
        the data-type.
    comments : str, optional
        The character used to indicate the start of a comment;
        default: '#'.
    delimiter : str, optional
        The string used to separate values.  By default, this is any
        whitespace.
    converters : dict, optional
        A dictionary mapping column number to a function that will convert
        that column to a float.  E.g., if column 0 is a date string:
        ``converters = {0: datestr2num}``.  Converters can also be used to
        provide a default value for missing data (but see also `genfromtxt`):
        ``converters = {3: lambda s: float(s.strip() or 0)}``.  Default: None.
    skiprows : int, optional
        Skip the first `skiprows` lines; default: 0.
    usecols : sequence, optional
        Which columns to read, with 0 being the first.  For example,
        ``usecols = (1,4,5)`` will extract the 2nd, 5th and 6th columns.
        The default, None, results in all columns being read.
    unpack : bool, optional
        If True, the returned array is transposed, so that arguments may be
        unpacked using ``x, y, z = loadtxt(...)``.  When used with a record
        data-type, arrays are returned for each field.  Default is False.
    ndmin : int, optional
        The returned array will have at least `ndmin` dimensions.
        Otherwise mono-dimensional axes will be squeezed.
        Legal values: 0 (default), 1 or 2.

        .. versionadded:: 1.6.0

    Returns
    -------
    out : ndarray
        Data read from the text file.

    See Also
    --------
    load, fromstring, fromregex
    genfromtxt : Load data with missing values handled as specified.
    scipy.io.loadmat : reads MATLAB data files

    Notes
    -----
    This function aims to be a fast reader for simply formatted files.  The
    `genfromtxt` function provides more sophisticated handling of, e.g.,
    lines with missing values.

    Examples
    --------
    >>> from StringIO import StringIO   # StringIO behaves like a file object
    >>> c = StringIO("0 1\\n2 3")
    >>> np.loadtxt(c)
    array([[ 0.,  1.],
           [ 2.,  3.]])

    >>> d = StringIO("M 21 72\\nF 35 58")
    >>> np.loadtxt(d, dtype={'names': ('gender', 'age', 'weight'),
    ...                      'formats': ('S1', 'i4', 'f4')})
    array([('M', 21, 72.0), ('F', 35, 58.0)],
          dtype=[('gender', '|S1'), ('age', '<i4'), ('weight', '<f4')])

    >>> c = StringIO("1,0,2\\n3,0,4")
    >>> x, y = np.loadtxt(c, delimiter=',', usecols=(0, 2), unpack=True)
    >>> x
    array([ 1.,  3.])
    >>> y
    array([ 2.,  4.])

    """
    # Type conversions for Py3 convenience
    comments = asbytes(comments)
    user_converters = converters
    if delimiter is not None:
        delimiter = asbytes(delimiter)
    if usecols is not None:
        usecols = list(usecols)

    fown = False
    try:
        if _is_string_like(fname):
            fown = True
            if fname.endswith('.gz'):
                fh = iter(seek_gzip_factory(fname))
            elif fname.endswith('.bz2'):
                import bz2
                fh = iter(bz2.BZ2File(fname))
            elif sys.version_info[0] == 2:
                fh = iter(open(fname, 'U'))
            else:
                fh = iter(open(fname))
        else:
            fh = iter(fname)
    except TypeError:
        raise ValueError('fname must be a string, file handle, or generator')
    X = []

    def flatten_dtype(dt):
        """Unpack a structured data-type, and produce re-packing info."""
        if dt.names is None:
            # If the dtype is flattened, return.
            # If the dtype has a shape, the dtype occurs
            # in the list more than once.
            shape = dt.shape
            if len(shape) == 0:
                return ([dt.base], None)
            else:
                packing = [(shape[-1], list)]
                if len(shape) > 1:
                    for dim in dt.shape[-2::-1]:
                        packing = [(dim*packing[0][0], packing*dim)]
                return ([dt.base] * int(np.prod(dt.shape)), packing)
        else:
            types = []
            packing = []
            for field in dt.names:
                tp, bytes = dt.fields[field]
                flat_dt, flat_packing = flatten_dtype(tp)
                types.extend(flat_dt)
                # Avoid extra nesting for subarrays
                if len(tp.shape) > 0:
                    packing.extend(flat_packing)
                else:
                    packing.append((len(flat_dt), flat_packing))
            return (types, packing)

    def pack_items(items, packing):
        """Pack items into nested lists based on re-packing info."""
        if packing is None:
            return items[0]
        elif packing is tuple:
            return tuple(items)
        elif packing is list:
            return list(items)
        else:
            start = 0
            ret = []
            for length, subpacking in packing:
                ret.append(pack_items(items[start:start+length], subpacking))
                start += length
            return tuple(ret)

    def split_line(line):
        """Chop off comments, strip, and split at delimiter."""
        line = asbytes(line).split(comments)[0].strip(asbytes('\r\n'))
        if line:
            return line.split(delimiter)
        else:
            return []

    try:
        # Make sure we're dealing with a proper dtype
        dtype = np.dtype(dtype)
        defconv = _getconv(dtype)

        # Skip the first `skiprows` lines
        for i in range(skiprows):
            next(fh)

        # Read until we find a line with some values, and use
        # it to estimate the number of columns, N.
        first_vals = None
        try:
            while not first_vals:
                first_line = next(fh)
                first_vals = split_line(first_line)
        except StopIteration:
            # End of lines reached
            first_line = ''
            first_vals = []
            warnings.warn('loadtxt: Empty input file: "%s"' % fname)
        N = len(usecols or first_vals)

        dtype_types, packing = flatten_dtype(dtype)
        if len(dtype_types) > 1:
            # We're dealing with a structured array, each field of
            # the dtype matches a column
            converters = [_getconv(dt) for dt in dtype_types]
        else:
            # All fields have the same dtype
            converters = [defconv for i in range(N)]
            if N > 1:
                packing = [(N, tuple)]

        # By preference, use the converters specified by the user
        for i, conv in (user_converters or {}).items():
            if usecols:
                try:
                    i = usecols.index(i)
                except ValueError:
                    # Unused converter specified
                    continue
            converters[i] = conv

        # Parse each line, including the first
        for i, line in enumerate(itertools.chain([first_line], fh)):
            vals = split_line(line)
            if len(vals) == 0:
                continue
            if usecols:
                vals = [vals[i] for i in usecols]
            if len(vals) != N:
                line_num = i + skiprows + 1
                raise ValueError("Wrong number of columns at line %d"
                                 % line_num)

            # Convert each value according to its column and store
            items = [conv(val) for (conv, val) in zip(converters, vals)]
            # Then pack it according to the dtype's nesting
            items = pack_items(items, packing)
            X.append(items)
    finally:
        if fown:
            fh.close()

    X = np.array(X, dtype)
    # Multicolumn data are returned with shape (1, N, M), i.e.
    # (1, 1, M) for a single row - remove the singleton dimension there
    if X.ndim == 3 and X.shape[:2] == (1, 1):
        X.shape = (1, -1)

    # Verify that the array has at least dimensions `ndmin`.
    # Check correctness of the values of `ndmin`
    if not ndmin in [0, 1, 2]:
        raise ValueError('Illegal value of ndmin keyword: %s' % ndmin)
    # Tweak the size and shape of the arrays - remove extraneous dimensions
    if X.ndim > ndmin:
        X = np.squeeze(X)
    # and ensure we have the minimum number of dimensions asked for
    # - has to be in this order for the odd case ndmin=1, X.squeeze().ndim=0
    if X.ndim < ndmin:
        if ndmin == 1:
            X = np.atleast_1d(X)
        elif ndmin == 2:
            X = np.atleast_2d(X).T

    if unpack:
        if len(dtype_types) > 1:
            # For structured arrays, return an array for each field.
            return [X[field] for field in dtype.names]
        else:
            return X.T
    else:
        return X