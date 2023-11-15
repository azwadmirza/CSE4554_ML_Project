    def match(self, segments, parse_context):
        elem = self._get_elem(dialect=parse_context.dialect)

        if elem:
            # Match against that. NB We're not incrementing the match_depth here.
            # References shouldn't relly count as a depth of match.
            return elem._match(
                segments=segments,
                parse_context=parse_context.copy(match_segment=self._get_ref()))
        else:
            raise ValueError("Null Element returned! _elements: {0!r}".format(self._elements))