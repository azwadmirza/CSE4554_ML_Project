    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """ ReSegment implements it's own matching function,
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. This only matches on a single segment."""
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]
        # Regardless of what we're passed, make a string.
        # NB: We only match on the first element of a set of segments.
        s = segments[0].raw
        # Deal with case sentitivity
        if not cls._case_sensitive:
            sc = s.upper()
        else:
            sc = s
        if len(s) == 0:
            raise ValueError("Zero length string passed to ReSegment!?")
        logging.debug("[PD:{0} MD:{1}] (RE) {2}.match considering {3!r} against {4!r}".format(
            parse_depth, match_depth, cls.__name__, sc, cls._template))
        # Try the regex
        result = re.match(cls._template, sc)
        if result:
            r = result.group(0)
            # Check that we've fully matched
            if r == sc:
                m = cls(raw=s, pos_marker=segments[0].pos_marker),  # Return a tuple
                return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)