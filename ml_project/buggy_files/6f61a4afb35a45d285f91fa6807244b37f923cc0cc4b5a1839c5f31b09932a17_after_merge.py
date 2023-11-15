    def match(cls, segments, parse_context):
        """ NamedSegment implements it's own matching function,
        we assume that ._template is the `name` of a segment"""
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We only match on the first element of a set of segments
        if len(segments) >= 1:
            s = segments[0]
            if not cls._case_sensitive:
                n = s.name.upper()
            else:
                n = s.name
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_context.parse_depth, parse_context.match_depth, cls.__name__, n, cls._template))
            if cls._template == n:
                m = cls(raw=s.raw, pos_marker=segments[0].pos_marker),  # Return a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)