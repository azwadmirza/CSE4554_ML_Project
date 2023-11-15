def split_argument(req, short=None, long_=None):
    """Split an argument from a string (finds None if not present).

    Uses -short <arg>, --long <arg>, and --long=arg as permutations.

    returns string, index
    """
    index_entries = []
    if long_:
        long_ = ' --{0}'.format(long_)
        index_entries.extend(['{0}{1}'.format(long_, s) for s in [' ', '=']])
    if short:
        index_entries.append(' -{0} '.format(short))
    index = None
    index_entry = first([entry for entry in index_entries if entry in req])
    if index_entry:
        req, index = req.split(index_entry)
        remaining_line = index.split()
        if len(remaining_line) > 1:
            index, more_req = remaining_line[0], ' '.join(remaining_line[1:])
            req = '{0} {1}'.format(req, more_req)
    return req, index