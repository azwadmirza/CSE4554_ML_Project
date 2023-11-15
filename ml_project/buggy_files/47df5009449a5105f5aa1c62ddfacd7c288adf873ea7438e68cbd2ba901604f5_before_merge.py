def hy_parse(source, filename='<string>'):
    """Parse a Hy source string.

    Parameters
    ----------
    source: string
        Source code to parse.

    filename: string, optional
        File name corresponding to source.  Defaults to "<string>".

    Returns
    -------
    out : HyExpression
    """
    _source = re.sub(r'\A#!.*', '', source)
    try:
        res = HyExpression([HySymbol("do")] +
                           tokenize(_source + "\n",
                                    filename=filename))
        res.source = source
        res.filename = filename
        return res
    except HySyntaxError as e:
        reraise(type(e), e, None)