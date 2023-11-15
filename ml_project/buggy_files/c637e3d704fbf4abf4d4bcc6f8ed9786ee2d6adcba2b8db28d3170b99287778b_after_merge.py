def _shortcut_open(uri, mode, **kw):
    """Try to open the URI using the standard library io.open function.

    This can be much faster than the alternative of opening in binary mode and
    then decoding.

    This is only possible under the following conditions:

        1. Opening a local file
        2. Ignore extension is set to True

    If it is not possible to use the built-in open for the specified URI, returns None.

    :param str uri: A string indicating what to open.
    :param str mode: The mode to pass to the open function.
    :param dict kw:
    :returns: The opened file
    :rtype: file
    """
    if not isinstance(uri, six.string_types):
        return None

    parsed_uri = _parse_uri(uri)
    if parsed_uri.scheme != 'file':
        return None

    _, extension = P.splitext(parsed_uri.uri_path)
    ignore_extension = kw.get('ignore_extension', False)
    if extension in ('.gz', '.bz2') and not ignore_extension:
        return None

    #
    # https://docs.python.org/2/library/functions.html#open
    #
    # buffering: 0: off; 1: on; negative number: use system default
    #
    buffering = kw.get('buffering', -1)

    open_kwargs = {}
    errors = kw.get('errors')
    if errors is not None:
        open_kwargs['errors'] = errors

    encoding = kw.get('encoding')
    if encoding is not None:
        open_kwargs['encoding'] = encoding
        mode = mode.replace('b', '')

    #
    # Under Py3, the built-in open accepts kwargs, and it's OK to use that.
    # Under Py2, the built-in open _doesn't_ accept kwargs, but we still use it
    # whenever possible (see issue #207).  If we're under Py2 and have to use
    # kwargs, then we have no option other to use io.open.
    #
    if six.PY3:
        return open(parsed_uri.uri_path, mode, buffering=buffering, **open_kwargs)
    elif not open_kwargs:
        return open(parsed_uri.uri_path, mode, buffering=buffering)
    return io.open(parsed_uri.uri_path, mode, buffering=buffering, **open_kwargs)