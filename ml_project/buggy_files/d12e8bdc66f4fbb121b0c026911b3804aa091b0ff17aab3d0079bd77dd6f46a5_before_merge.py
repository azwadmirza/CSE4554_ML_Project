def _loadarff(ofile):
    # Parse the header file
    try:
        rel, attr = read_header(ofile)
    except ValueError as e:
        msg = "Error while parsing header, error was: " + str(e)
        raise ParseArffError(msg)

    # Check whether we have a string attribute (not supported yet)
    hasstr = False
    for name, value in attr:
        type = parse_type(value)
        if type == 'string':
            hasstr = True

    meta = MetaData(rel, attr)

    # XXX The following code is not great
    # Build the type descriptor descr and the list of convertors to convert
    # each attribute to the suitable type (which should match the one in
    # descr).

    # This can be used once we want to support integer as integer values and
    # not as numeric anymore (using masked arrays ?).
    acls2dtype = {'real': float, 'integer': float, 'numeric': float}
    acls2conv = {'real': safe_float, 'integer': safe_float, 'numeric': safe_float}
    descr = []
    convertors = []
    if not hasstr:
        for name, value in attr:
            type = parse_type(value)
            if type == 'date':
                date_format, datetime_unit = get_date_format(value)
                descr.append((name, "datetime64[%s]" % datetime_unit))
                convertors.append(partial(safe_date, date_format=date_format, datetime_unit=datetime_unit))
            elif type == 'nominal':
                n = maxnomlen(value)
                descr.append((name, 'S%d' % n))
                pvalue = get_nom_val(value)
                convertors.append(partial(safe_nominal, pvalue=pvalue))
            else:
                descr.append((name, acls2dtype[type]))
                convertors.append(safe_float)
                #dc.append(acls2conv[type])
                #sdescr.append((name, acls2sdtype[type]))
    else:
        # How to support string efficiently ? Ideally, we should know the max
        # size of the string before allocating the numpy array.
        raise NotImplementedError("String attributes not supported yet, sorry")

    ni = len(convertors)

    # Get the delimiter from the first line of data:
    def next_data_line(row_iter):
        """Assumes we are already in the data part (eg after @data)."""
        raw = next(row_iter)
        while r_empty.match(raw) or r_comment.match(raw):
            raw = next(row_iter)
        return raw

    try:
        try:
            dtline = next_data_line(ofile)
            delim = get_delim(dtline)
        except ValueError as e:
            raise ParseArffError("Error while parsing delimiter: " + str(e))
    finally:
        ofile.seek(0, 0)
        ofile = go_data(ofile)
        # skip the @data line
        next(ofile)

    def generator(row_iter, delim=','):
        # TODO: this is where we are spending times (~80%). I think things
        # could be made more efficiently:
        #   - We could for example "compile" the function, because some values
        #   do not change here.
        #   - The function to convert a line to dtyped values could also be
        #   generated on the fly from a string and be executed instead of
        #   looping.
        #   - The regex are overkill: for comments, checking that a line starts
        #   by % should be enough and faster, and for empty lines, same thing
        #   --> this does not seem to change anything.

        # We do not abstract skipping comments and empty lines for performances
        # reason.
        raw = next(row_iter)
        while r_empty.match(raw) or r_comment.match(raw):
            raw = next(row_iter)

        # 'compiling' the range since it does not change
        # Note, I have already tried zipping the converters and
        # row elements and got slightly worse performance.
        elems = list(range(ni))

        row = raw.split(delim)
        yield tuple([convertors[i](row[i]) for i in elems])
        for raw in row_iter:
            while r_comment.match(raw) or r_empty.match(raw):
                raw = next(row_iter)
            row = raw.split(delim)
            yield tuple([convertors[i](row[i]) for i in elems])

    a = generator(ofile, delim=delim)
    # No error should happen here: it is a bug otherwise
    data = np.fromiter(a, descr)
    return data, meta