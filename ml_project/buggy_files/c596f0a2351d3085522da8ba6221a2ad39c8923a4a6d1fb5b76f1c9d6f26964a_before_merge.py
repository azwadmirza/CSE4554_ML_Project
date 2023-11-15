    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        elem = self._get_elem(dialect=dialect)

        if elem:
            # Match against that. NB We're not incrementing the match_depth here.
            # References shouldn't relly count as a depth of match.
            match_segment = self._get_ref()
            return elem._match(
                segments=segments, match_depth=match_depth,
                parse_depth=parse_depth, verbosity=verbosity,
                dialect=dialect, match_segment=match_segment)
        else:
            raise ValueError("Null Element returned! _elements: {0!r}".format(self._elements))