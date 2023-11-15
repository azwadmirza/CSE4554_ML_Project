    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        if self.code_only:
            first_code_idx = None
            # Work through to find the first code segment...
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    first_code_idx = idx
                    break
            else:
                # We've trying to match on a sequence of segments which contain no code.
                # That means this isn't a match.
                return MatchResult.from_unmatched(segments)

            match = self.target._match(
                segments=segments[first_code_idx:], match_depth=match_depth + 1,
                parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                match_segment=match_segment)
            if match:
                # The match will probably have returned a mutated version rather
                # that the raw segment sent for matching. We need to reinsert it
                # back into the sequence in place of the raw one, but we can't
                # just assign at the index because it's a tuple and not a list.
                # to get around that we do this slightly more elaborate construction.

                # NB: This match may be partial or full, either is cool. In the case
                # of a partial match, given that we're only interested in what it STARTS
                # with, then we can still used the unmatched parts on the end.
                # We still need to deal with any non-code segments at the start.
                if self.terminator:
                    # We have an optional terminator. We should only match up to when
                    # this matches. This should also respect bracket counting.
                    match_segments = match.matched_segments
                    trailing_segments = match.unmatched_segments

                    # Given a set of segments, iterate through looking for
                    # a terminator.
                    term_match = self.bracket_sensitive_forward_match(
                        segments=trailing_segments,
                        start_bracket=self.start_bracket,
                        end_bracket=self.end_bracket,
                        match_depth=match_depth,
                        parse_depth=parse_depth,
                        verbosity=verbosity,
                        terminator=self.terminator,
                        dialect=dialect,
                        match_segment=match_segment
                    )
                    return MatchResult(
                        segments[:first_code_idx]
                        + match_segments
                        + term_match.matched_segments,
                        term_match.unmatched_segments,
                    )
                else:
                    return MatchResult.from_matched(
                        segments[:first_code_idx]
                        + match.matched_segments
                        + match.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")