    def match(self, segments, parse_context):
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
                segments=segments[first_code_idx:],
                parse_context=parse_context.copy(incr='match_depth'))
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
                    res = self._bracket_sensitive_look_ahead_match(
                        segments=trailing_segments, matchers=[self.terminator],
                        parse_context=parse_context
                    )

                    # Depending on whether we found a terminator or not we treat
                    # the result slightly differently. If no terminator was found,
                    # we just use the whole unmatched segment. If we did find one,
                    # we match up until (but not including) that terminator.
                    term_match = res[1]
                    if term_match:
                        m_tail = res[0]
                        u_tail = term_match.all_segments()
                    else:
                        m_tail = term_match.unmatched_segments
                        u_tail = ()

                    return MatchResult(
                        segments[:first_code_idx]
                        + match_segments
                        + m_tail,
                        u_tail,
                    )
                else:
                    return MatchResult.from_matched(
                        segments[:first_code_idx]
                        + match.all_segments())
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")