    def match(self, segments, parse_context):
        """
        Matching for GreedyUntil works just how you'd expect.
        """

        pre, mat, _ = self._bracket_sensitive_look_ahead_match(
            segments, self._elements, parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)

        # Do we have a match?
        if mat:
            # Return everything up to the match
            return MatchResult(pre, mat.all_segments())
        else:
            # Return everything
            return MatchResult.from_matched(segments)