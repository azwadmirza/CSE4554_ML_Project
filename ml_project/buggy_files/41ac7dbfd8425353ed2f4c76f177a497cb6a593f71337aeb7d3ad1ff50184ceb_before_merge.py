def join(*parts, **kwargs):
    '''
    This functions tries to solve some issues when joining multiple absolute
    paths on both *nix and windows platforms.

    See tests/unit/utils/path_join_test.py for some examples on what's being
    talked about here.

    The "use_posixpath" kwarg can be be used to force joining using poxixpath,
    which is useful for Salt fileserver paths on Windows masters.
    '''
    if six.PY3:
        new_parts = []
        for part in parts:
            new_parts.append(salt.utils.stringutils.to_str(part))
        parts = new_parts

    kwargs = salt.utils.args.clean_kwargs(**kwargs)
    use_posixpath = kwargs.pop('use_posixpath', False)
    if kwargs:
        salt.utils.args.invalid_kwargs(kwargs)

    pathlib = posixpath if use_posixpath else os.path

    # Normalize path converting any os.sep as needed
    parts = [pathlib.normpath(p) for p in parts]

    try:
        root = parts.pop(0)
    except IndexError:
        # No args passed to func
        return ''

    if not parts:
        ret = root
    else:
        stripped = [p.lstrip(os.sep) for p in parts]
        try:
            ret = pathlib.join(root, *stripped)
        except UnicodeDecodeError:
            # This is probably Python 2 and one of the parts contains unicode
            # characters in a bytestring. First try to decode to the system
            # encoding.
            try:
                enc = __salt_system_encoding__
            except NameError:
                enc = sys.stdin.encoding or sys.getdefaultencoding()
            try:
                ret = pathlib.join(root.decode(enc),
                                   *[x.decode(enc) for x in stripped])
            except UnicodeDecodeError:
                # Last resort, try UTF-8
                ret = pathlib.join(root.decode('UTF-8'),
                                   *[x.decode('UTF-8') for x in stripped])
    return pathlib.normpath(ret)