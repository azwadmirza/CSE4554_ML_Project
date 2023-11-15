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
    from pandas.util.clipboard import clipboard_set
    if excel is None:
        excel = True

    if excel:
        try:
            if sep is None:
                sep = '\t'
            buf = StringIO()
            obj.to_csv(buf, sep=sep, **kwargs)
            clipboard_set(buf.getvalue())
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