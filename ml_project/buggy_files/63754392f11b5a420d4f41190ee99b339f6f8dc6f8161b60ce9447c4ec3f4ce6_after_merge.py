    def match(cls, segments, parse_context):
        """ Keyword implements it's own matching function """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We're only going to match against the first element
        if len(segments) >= 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            if cls._case_sensitive:
                raw_comp = raw
            else:
                raw_comp = raw.upper()
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_context.parse_depth, parse_context.match_depth, cls.__name__, raw_comp, cls._template))
            if cls._template == raw_comp:
                m = cls(raw=raw, pos_marker=pos),  # Return as a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)