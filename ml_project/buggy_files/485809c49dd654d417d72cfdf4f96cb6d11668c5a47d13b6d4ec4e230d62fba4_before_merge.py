    def _expand_hostpattern(self, hostpattern):
        '''
        Takes a single host pattern and returns a list of hostnames and an
        optional port number that applies to all of them.
        '''

        # Can the given hostpattern be parsed as a host with an optional port
        # specification?

        (pattern, port) = parse_address(hostpattern, allow_ranges=True)
        if not pattern:
            self._raise_error("Can't parse '%s' as host[:port]" % hostpattern)

        # Once we have separated the pattern, we expand it into list of one or
        # more hostnames, depending on whether it contains any [x:y] ranges.

        if detect_range(pattern):
            hostnames = expand_hostname_range(pattern)
        else:
            hostnames = [pattern]

        return (hostnames, port)