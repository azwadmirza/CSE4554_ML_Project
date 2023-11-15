    def parse(self, recurse=True, parse_depth=0, verbosity=0, dialect=None):
        """ Use the parse kwarg for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels """

        # We should call the parse grammar on this segment, which calls
        # the match grammar on all it's children.

        if not dialect:
            raise RuntimeError("No dialect provided to {0!r}!".format(self))

        # the parse_depth and recurse kwargs control how deep we will recurse for testing.
        if not self.segments:
            # This means we're a root segment, just return an unmutated self
            return self

        # Get the Parse Grammar
        g = self._parse_grammar()
        if g is None:
            logging.debug("{0}.parse: no grammar. returning".format(self.__class__.__name__))
            return self
        # Use the Parse Grammar (and the private method)
        # NOTE: No match_depth kwarg, because this is the start of the matching.
        m = g._match(
            segments=self.segments, parse_depth=parse_depth, verbosity=verbosity,
            dialect=dialect, match_segment=self.__class__.__name__)

        # Calling unify here, allows the MatchResult class to do all the type checking.
        try:
            m = MatchResult.unify(m)
        except TypeError as err:
            logging.error(
                "[PD:{0}] {1}.parse. Error on unifying result of match grammar!".format(
                    parse_depth, self.__class__.__name__))
            raise err

        # Basic Validation, that we haven't dropped anything.
        check_still_complete(self.segments, m.matched_segments, m.unmatched_segments)

        if m.has_match():
            if m.is_complete():
                # Complete match, happy days!
                self.segments = m.matched_segments
            else:
                # Incomplete match.
                # For now this means the parsing has failed. Lets add the unmatched bit at the
                # end as something unparsable.
                # TODO: Do something more intelligent here.
                self.segments = m.matched_segments + (UnparsableSegment(
                    segments=m.unmatched_segments, expected="Nothing..."),)
        else:
            # If there's no match at this stage, then it's unparsable. That's
            # a problem at this stage so wrap it in an unparable segment and carry on.
            self.segments = UnparsableSegment(segments=self.segments, expected=g.expected_string(dialect=dialect)),  # NB: tuple

        # Validate new segments
        self.validate_segments(text="parsing")

        # Recurse if allowed (using the expand method to deal with the expansion)
        logging.debug(
            "{0}.parse: Done Parse. Plotting Recursion. Recurse={1!r}".format(
                self.__class__.__name__, recurse))
        parse_depth_msg = "###\n#\n# Beginning Parse Depth {0}: {1}\n#\n###\nInitial Structure:\n{2}".format(
            parse_depth + 1, self.__class__.__name__, self.stringify())
        if recurse is True:
            logging.debug(parse_depth_msg)
            self.segments = self.expand(self.segments, recurse=True, parse_depth=parse_depth + 1,
                                        verbosity=verbosity, dialect=dialect)
        elif isinstance(recurse, int):
            if recurse > 1:
                logging.debug(parse_depth_msg)
                self.segments = self.expand(self.segments, recurse=recurse - 1, parse_depth=parse_depth + 1,
                                            verbosity=verbosity, dialect=dialect)

        # Validate new segments
        self.validate_segments(text="expanding")

        return self