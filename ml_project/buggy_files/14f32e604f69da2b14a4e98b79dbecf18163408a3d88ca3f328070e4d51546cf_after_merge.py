def parse_address(address, allow_ranges=False):
    """
    Takes a string and returns a (host, port) tuple. If the host is None, then
    the string could not be parsed as a host identifier with an optional port
    specification. If the port is None, then no port was specified.

    The host identifier may be a hostname (qualified or not), an IPv4 address,
    or an IPv6 address. If allow_ranges is True, then any of those may contain
    [x:y] range specifications, e.g. foo[1:3] or foo[0:5]-bar[x-z].

    The port number is an optional :NN suffix on an IPv4 address or host name,
    or a mandatory :NN suffix on any square-bracketed expression: IPv6 address,
    IPv4 address, or host name. (This means the only way to specify a port for
    an IPv6 address is to enclose it in square brackets.)
    """

    # First, we extract the port number if one is specified.

    port = None
    for matching in ['bracketed_hostport', 'hostport']:
        m = patterns[matching].match(address)
        if m:
            (address, port) = m.groups()
            port = int(port)
            continue

    # What we're left with now must be an IPv4 or IPv6 address, possibly with
    # numeric ranges, or a hostname with alphanumeric ranges.

    host = None
    for matching in ['ipv4', 'ipv6', 'hostname']:
        m = patterns[matching].match(address)
        if m:
            host = address
            continue

    # If it isn't any of the above, we don't understand it.
    if not host:
        raise AnsibleError("Not a valid network hostname: %s" % address)

    # If we get to this point, we know that any included ranges are valid.
    # If the caller is prepared to handle them, all is well.
    # Otherwise we treat it as a parse failure.
    if not allow_ranges and '[' in host:
        raise AnsibleParserError("Detected range in host but was asked to ignore ranges")

    return (host, port)