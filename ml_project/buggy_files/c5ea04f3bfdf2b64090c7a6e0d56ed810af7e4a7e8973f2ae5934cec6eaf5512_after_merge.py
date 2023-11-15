def parse_file_desc(file_desc):
    """Parse file description returning pair (host_info, filename)

    In other words, bescoto@folly.stanford.edu::/usr/bin/ls =>
    ("bescoto@folly.stanford.edu", "/usr/bin/ls").  The
    complication is to allow for quoting of : by a \\.  If the
    string is not separated by :, then the host_info is None.

    """

    # paths and similar objects must always be bytes
    file_desc = os.fsencode(file_desc)
    # match double colon not preceded by an odd number of backslashes
    file_match = re.fullmatch(rb"^(?P<host>.*[^\\](?:\\\\)*)::(?P<path>.*)$",
                              file_desc)
    if file_match:
        file_host = file_match.group("host")
        # According to description, the backslashes must be unquoted, i.e.
        # double backslashes replaced by single ones, and single ones removed.
        # Hence we split along double ones, remove single ones in each element,
        # and join back with a single backslash.
        file_host = b'\\'.join(
            [x.replace(b'\\', b'') for x in re.split(rb'\\\\', file_host) if x])
        file_path = file_match.group("path")
    else:
        if re.match(rb"^::", file_desc):
            raise SetConnectionsException("No file host in '%s'" % file_desc)
        file_host = None
        file_path = file_desc

    # make sure paths under Windows use / instead of \
    if os.path.altsep:  # only Windows has an alternative separator for paths
        file_path = file_path.replace(os.fsencode(os.path.sep), b'/')

    if not file_path:
        raise SetConnectionsException("No file path in '%s'" % file_desc)

    return (file_host, file_path)