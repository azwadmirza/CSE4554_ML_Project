    def _match(cls, segments, parse_context):
        """ A wrapper on the match function to do some basic validation and logging """
        parse_match_logging(
            cls.__name__, '_match', 'IN', parse_context=parse_context,
            v_level=4, ls=len(segments))

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

        m = cls.match(segments, parse_context=parse_context)

        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    cls.__name__, type(m)))

        parse_match_logging(
            cls.__name__, '_match', 'OUT',
            parse_context=parse_context, v_level=4, m=m)
        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m