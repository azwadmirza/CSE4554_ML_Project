def read_clipboard(**kwargs):  # pragma: no cover
    """
    Read text from clipboard and pass to read_table. See read_table for the
    full argument list

    If unspecified, `sep` defaults to '\s+'

    Returns
    -------
    parsed : DataFrame
    """
    from pandas.util.clipboard import clipboard_get
    from pandas.io.parsers import read_table
    text = clipboard_get()

    # try to decode (if needed on PY3)
    # Strange. linux py33 doesn't complain, win py33 does
    if compat.PY3:
        try:
            text = compat.bytes_to_str(
                text, encoding=(kwargs.get('encoding') or
                                get_option('display.encoding'))
            )
        except:
            pass

    # Excel copies into clipboard with \t seperation
    # inspect no more then the 10 first lines, if they
    # all contain an equal number (>0) of tabs, infer
    # that this came from excel and set 'sep' accordingly
    lines = text[:10000].split('\n')[:-1][:10]

    # Need to remove leading white space, since read_table
    # accepts:
    #    a  b
    # 0  1  2
    # 1  3  4

    counts = set([x.lstrip().count('\t') for x in lines])
    if len(lines) > 1 and len(counts) == 1 and counts.pop() != 0:
        kwargs['sep'] = '\t'

    if kwargs.get('sep') is None and kwargs.get('delim_whitespace') is None:
        kwargs['sep'] = '\s+'

    return read_table(StringIO(text), **kwargs)