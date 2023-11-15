def split_argument(req, short=None, long_=None, num=-1):
    """Split an argument from a string (finds None if not present).

    Uses -short <arg>, --long <arg>, and --long=arg as permutations.

    returns string, index
    """
    index_entries = []
    import re
    if long_:
        index_entries.append('--{0}'.format(long_))
    if short:
        index_entries.append('-{0}'.format(short))
    match_string = '|'.join(index_entries)
    matches = re.findall('(?<=\s)({0})([\s=])(\S+)'.format(match_string), req)
    remove_strings = []
    match_values = []
    for match in matches:
        match_values.append(match[-1])
        remove_strings.append(''.join(match))
    for string_to_remove in remove_strings:
        req = req.replace(' {0}'.format(string_to_remove), '')
    if not match_values:
        return req, None
    if num == 1:
        return req, match_values[0]
    if num == -1:
        return req, match_values
    return req, match_values[:num]