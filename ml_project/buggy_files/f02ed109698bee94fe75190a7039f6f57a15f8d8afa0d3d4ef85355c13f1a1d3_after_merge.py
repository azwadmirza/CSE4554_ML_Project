    def match(cls, segments, parse_context):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        if cls._match_grammar():
            # Call the private method
            m = cls._match_grammar()._match(segments=segments, parse_context=parse_context.copy(incr='match_depth'))

            # Calling unify here, allows the MatchResult class to do all the type checking.
            try:
                m = MatchResult.unify(m)
            except TypeError as err:
                logging.error(
                    "[PD:{0} MD:{1}] {2}.match. Error on unifying result of match grammar!".format(
                        parse_context.parse_depth, parse_context.match_depth, cls.__name__))
                raise err

            # Once unified we can deal with it just as a MatchResult
            if m.has_match():
                return MatchResult((cls(segments=m.matched_segments),), m.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))