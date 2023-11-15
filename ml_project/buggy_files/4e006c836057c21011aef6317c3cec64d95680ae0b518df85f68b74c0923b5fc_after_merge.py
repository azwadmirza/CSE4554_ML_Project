    def match(self, segments, parse_context):
        # Match on each of the options
        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments
        n_matches = 0
        while True:
            if self.max_times and n_matches >= self.max_times:
                # We've matched as many times as we can
                return MatchResult(matched_segments.matched_segments, unmatched_segments)

            # Is there anything left to match?
            if len(unmatched_segments) == 0:
                # No...
                if n_matches >= self.min_times:
                    return MatchResult(matched_segments.matched_segments, unmatched_segments)
                else:
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)

            # Is the next segment code?
            if self.code_only and not unmatched_segments[0].is_code:
                # We should add this one to the match and carry on
                matched_segments += unmatched_segments[0],
                unmatched_segments = unmatched_segments[1:]
                check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                continue

            # Try the possibilities
            for opt in self._elements:
                m = opt._match(
                    unmatched_segments,
                    parse_context=parse_context.copy(incr='match_depth')
                )
                if m.has_match():
                    matched_segments += m.matched_segments
                    unmatched_segments = m.unmatched_segments
                    n_matches += 1
                    # Break out of the for loop which cycles us round
                    break
            else:
                # If we get here, then we've not managed to match. And the next
                # unmatched segments are meaningful, i.e. they're not what we're
                # looking for.
                if n_matches >= self.min_times:
                    return MatchResult(matched_segments.matched_segments, unmatched_segments)
                else:
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)