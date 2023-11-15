    def _match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """ A wrapper on the match function to do some basic validation """
        t0 = get_time()

        if isinstance(segments, BaseSegment):
            segments = segments,  # Make into a tuple for compatability
        if not isinstance(segments, tuple):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    self.__class__.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)

        if len(segments) == 0:
            logging.info("{0}.match, was passed zero length segments list. NB: {0} contains {1!r}".format(
                self.__class__.__name__, self._elements))

        # Work out the raw representation and curtail if long
        parse_match_logging(
            parse_depth, match_depth, match_segment, self.__class__.__name__,
            '_match', 'IN', verbosity=verbosity, v_level=self.v_level,
            le=len(self._elements), ls=len(segments),
            seg=join_segments_raw_curtailed(segments))

        m = self.match(segments, match_depth=match_depth, parse_depth=parse_depth,
                       verbosity=verbosity, dialect=dialect, match_segment=match_segment)

        if not isinstance(m, MatchResult):
            logging.warning(
                "{0}.match, returned {1} rather than MatchResult".format(
                    self.__class__.__name__, type(m)))

        dt = get_time() - t0
        if m.is_complete():
            msg = 'OUT ++'
        elif m:
            msg = 'OUT -'
        else:
            msg = 'OUT'

        parse_match_logging(
            parse_depth, match_depth, match_segment, self.__class__.__name__,
            '_match', msg, verbosity=verbosity, v_level=self.v_level, dt=dt, m=m)

        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m