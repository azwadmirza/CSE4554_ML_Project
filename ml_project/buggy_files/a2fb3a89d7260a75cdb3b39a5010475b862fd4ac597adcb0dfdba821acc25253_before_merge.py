    def _match(cls, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """ A wrapper on the match function to do some basic validation and logging """
        parse_match_logging(
            parse_depth, match_depth, match_segment, cls.__name__,
            '_match', 'IN', verbosity=verbosity, v_level=4, ls=len(segments))

        if isinstance(segments, BaseSegment):
            segments = segments,  # Make into a tuple for compatability

        if not isinstance(segments, tuple):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    cls.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)

        if len(segments) == 0:
            logging.info("{0}._match, was passed zero length segments list".format(cls.__name__))

        m = cls.match(segments, match_depth=match_depth, parse_depth=parse_depth,
                      verbosity=verbosity, dialect=dialect, match_segment=match_segment)

        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    cls.__name__, type(m)))

        parse_match_logging(
            parse_depth, match_depth, match_segment, cls.__name__,
            '_match', 'OUT', verbosity=verbosity, v_level=4, m=m)
        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m