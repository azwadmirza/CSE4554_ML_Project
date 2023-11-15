    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """
        Matching for GreedyUntil works just how you'd expect.
        """
        for idx, seg in enumerate(segments):
            for opt in self._elements:
                if opt._match(seg, match_depth=match_depth + 1, parse_depth=parse_depth,
                              verbosity=verbosity, dialect=dialect, match_segment=match_segment):
                    # We've matched something. That means we should return everything up to this point
                    return MatchResult(segments[:idx], segments[idx:])
                else:
                    continue
        else:
            # We've got to the end without matching anything, so return.
            # We don't need to keep track of the match results, because
            # if any of them were usable, then we wouldn't be returning
            # anyway.
            return MatchResult.from_matched(segments)