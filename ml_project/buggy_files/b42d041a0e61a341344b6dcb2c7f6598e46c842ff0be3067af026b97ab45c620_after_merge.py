def read_clipboard(sep='\s+', **kwargs):  # pragma: no cover
    r"""
    Read text from clipboard and pass to read_table. See read_table for the
    full argument list

    Parameters
    ----------
    sep : str, default '\s+'.
        A string or regex delimiter. The default of '\s+' denotes
        one or more whitespace characters.

    Returns
    -------
    parsed : DataFrame
    """
    encoding = kwargs.pop('encoding', 'utf-8')

    # only utf-8 is valid for passed value because that's what clipboard
    # supports
    if encoding is not None and encoding.lower().replace('-', '') != 'utf8':
        raise NotImplementedError(
            'reading from clipboard only supports utf-8 encoding')

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

    # Excel copies into clipboard with \t separation
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
        sep = '\t'

    if sep is None and kwargs.get('delim_whitespace') is None:
        sep = '\s+'

    return read_table(StringIO(text), sep=sep, **kwargs)