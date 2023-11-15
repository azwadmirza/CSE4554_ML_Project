    def split_host_pattern(cls, pattern):
        """
        Takes a string containing host patterns separated by commas (or a list
        thereof) and returns a list of single patterns (which may not contain
        commas). Whitespace is ignored.

        Also accepts ':' as a separator for backwards compatibility, but it is
        not recommended due to the conflict with IPv6 addresses and host ranges.

        Example: 'a,b[1], c[2:3] , d' -> ['a', 'b[1]', 'c[2:3]', 'd']
        """

        if isinstance(pattern, list):
            return list(itertools.chain(*map(cls.split_host_pattern, pattern)))

        if ';' in pattern:
            patterns = re.split('\s*;\s*', pattern)
            display.deprecated("Use ',' or ':' instead of ';' to separate host patterns")

        # If it's got commas in it, we'll treat it as a straightforward
        # comma-separated list of patterns.

        elif ',' in pattern:
            patterns = re.split('\s*,\s*', pattern)

        # If it doesn't, it could still be a single pattern. This accounts for
        # non-separator uses of colons: IPv6 addresses and [x:y] host ranges.
        else:
            (base, port) = parse_address(pattern, allow_ranges=True)
            if base:
                patterns = [pattern]

            # The only other case we accept is a ':'-separated list of patterns.
            # This mishandles IPv6 addresses, and is retained only for backwards
            # compatibility.

            else:
                patterns = re.findall(
                    r'''(?:             # We want to match something comprising:
                            [^\s:\[\]]  # (anything other than whitespace or ':[]'
                            |           # ...or...
                            \[[^\]]*\]  # a single complete bracketed expression)
                        )+              # occurring once or more
                    ''', pattern, re.X
                )

        return [p.strip() for p in patterns]