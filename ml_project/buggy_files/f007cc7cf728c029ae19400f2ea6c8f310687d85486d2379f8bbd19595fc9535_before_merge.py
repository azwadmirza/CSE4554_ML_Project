def parse_query_string(s, model_cls):
    """Given a beets query string, return the `Query` and `Sort` they
    represent.

    The string is split into components using shell-like syntax.
    """
    # A bug in Python < 2.7.3 prevents correct shlex splitting of
    # Unicode strings.
    # http://bugs.python.org/issue6988
    if isinstance(s, unicode):
        s = s.encode('utf8')
    parts = [p.decode('utf8') for p in shlex.split(s)]
    return parse_query_parts(parts, model_cls)