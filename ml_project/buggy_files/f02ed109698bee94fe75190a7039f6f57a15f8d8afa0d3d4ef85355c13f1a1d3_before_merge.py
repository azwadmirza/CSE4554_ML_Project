    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        if cls._match_grammar():
            # Call the private method
            m = cls._match_grammar()._match(segments=segments, match_depth=match_depth + 1,
                                            parse_depth=parse_depth, verbosity=verbosity,
                                            dialect=dialect, match_segment=match_segment)

            # Calling unify here, allows the MatchResult class to do all the type checking.
            try:
                m = MatchResult.unify(m)
            except TypeError as err:
                logging.error(
                    "[PD:{0} MD:{1}] {2}.match. Error on unifying result of match grammar!".format(
                        parse_depth, match_depth, cls.__name__))
                raise err

            # Once unified we can deal with it just as a MatchResult
            if m.has_match():
                return MatchResult((cls(segments=m.matched_segments),), m.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))