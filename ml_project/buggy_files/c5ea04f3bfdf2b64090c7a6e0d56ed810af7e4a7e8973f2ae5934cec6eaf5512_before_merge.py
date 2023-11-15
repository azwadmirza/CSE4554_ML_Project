def parse_file_desc(file_desc):
    """Parse file description returning pair (host_info, filename)

    In other words, bescoto@folly.stanford.edu::/usr/bin/ls =>
    ("bescoto@folly.stanford.edu", "/usr/bin/ls").  The
    complication is to allow for quoting of : by a \\.  If the
    string is not separated by :, then the host_info is None.

    """

    def check_len(i):
        if i >= len(file_desc):
            raise SetConnectionsException(
                "Unexpected end to file description %s" % file_desc)

    host_info_list, i, last_was_quoted = [], 0, None
    file_desc = os.fsencode(
        file_desc)  # paths and similar must always be bytes
    while 1:
        if i == len(file_desc):
            # make sure paths under Windows use / instead of \
            if os.path.altsep:  # only Windows has an alternative separator for paths
                file_desc = file_desc.replace(os.fsencode(os.path.sep), b'/')
            return (None, file_desc)

        if file_desc[i] == ord(
                '\\'):  # byte[n] is the numerical value hence ord
            i = i + 1
            check_len(i)
            last_was_quoted = 1
        elif (file_desc[i] == ord(":") and i > 0
              and file_desc[i - 1] == ord(":") and not last_was_quoted):
            host_info_list.pop()  # Remove last colon from name
            break
        else:
            last_was_quoted = None
        host_info_list.append(file_desc[i:i + 1])
        i = i + 1

    check_len(i + 1)

    filename = file_desc[i + 1:]
    # make sure paths under Windows use / instead of \
    if os.path.altsep:  # only Windows has an alternative separator for paths
        filename = filename.replace(os.fsencode(os.path.sep), b'/')

    return (b"".join(host_info_list), filename)