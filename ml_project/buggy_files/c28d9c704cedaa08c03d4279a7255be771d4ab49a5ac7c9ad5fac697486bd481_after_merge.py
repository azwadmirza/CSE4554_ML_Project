def to_clipboard(obj, excel=None, sep=None, **kwargs):  # pragma: no cover
    """
    Attempt to write text representation of object to the system clipboard
    The clipboard can be then pasted into Excel for example.

    Parameters
    ----------
    obj : the object to write to the clipboard
    excel : boolean, defaults to True
            if True, use the provided separator, writing in a csv
            format for allowing easy pasting into excel.
            if False, write a string representation of the object
            to the clipboard
    sep : optional, defaults to tab
    other keywords are passed to to_csv

    Notes
    -----
    Requirements for your platform
      - Linux: xclip, or xsel (with gtk or PyQt4 modules)
      - Windows:
      - OS X:
    """
    encoding = kwargs.pop('encoding', 'utf-8')

    # testing if an invalid encoding is passed to clipboard
    if encoding is not None and encoding.lower().replace('-', '') != 'utf8':
        raise ValueError('clipboard only supports utf-8 encoding')

    from pandas.util.clipboard import clipboard_set
    if excel is None:
        excel = True

    if excel:
        try:
            if sep is None:
                sep = '\t'
            buf = StringIO()
            # clipboard_set (pyperclip) expects unicode
            obj.to_csv(buf, sep=sep, encoding='utf-8', **kwargs)
            text = buf.getvalue()
            if PY2:
                text = text.decode('utf-8')
            clipboard_set(text)
            return
        except:
            pass

    if isinstance(obj, DataFrame):
        # str(df) has various unhelpful defaults, like truncation
        with option_context('display.max_colwidth', 999999):
            objstr = obj.to_string(**kwargs)
    else:
        objstr = str(obj)
    clipboard_set(objstr)