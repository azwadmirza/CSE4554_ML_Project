    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        # Rewrite of sequence. We should match FORWARD, this reduced duplication.
        # Sub-matchers should be greedy and so we can jsut work forward with each one.
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)
        # NB: We don't use seg_idx here because the submatchers may be mutating the length
        # of the remaining segments
        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments

        for idx, elem in enumerate(self._elements):
            while True:
                if len(unmatched_segments) == 0:
                    # We've run our of sequence without matching everyting.
                    # Do only optional elements remain.
                    if all([e.is_optional() for e in self._elements[idx:]]):
                        # then it's ok, and we can return what we've got so far.
                        # No need to deal with anything left over because we're at the end.
                        return matched_segments
                    else:
                        # we've got to the end of the sequence without matching all
                        # required elements.
                        return MatchResult.from_unmatched(segments)
                else:
                    # We're not at the end, first detect whitespace and then try to match.
                    if self.code_only and not unmatched_segments[0].is_code:
                        # We should add this one to the match and carry on
                        matched_segments += unmatched_segments[0],
                        unmatched_segments = unmatched_segments[1:]
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                        continue

                    # It's not whitespace, so carry on to matching
                    elem_match = elem._match(
                        unmatched_segments, match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                        match_segment=match_segment)

                    if elem_match.has_match():
                        # We're expecting mostly partial matches here, but complete
                        # matches are possible.
                        matched_segments += elem_match.matched_segments
                        unmatched_segments = elem_match.unmatched_segments
                        # Each time we do this, we do a sense check to make sure we haven't
                        # dropped anything. (Because it's happened before!).
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)

                        # Break out of the while loop and move to the next element.
                        break
                    else:
                        # If we can't match an element, we should ascertain whether it's
                        # required. If so then fine, move on, but otherwise we should crash
                        # out without a match. We have not matched the sequence.
                        if elem.is_optional():
                            # This will crash us out of the while loop and move us
                            # onto the next matching element
                            break
                        else:
                            return MatchResult.from_unmatched(segments)
        else:
            # If we get to here, we've matched all of the elements (or skipped them)
            # but still have some segments left (or perhaps have precisely zero left).
            # In either case, we're golden. Return successfully, with any leftovers as
            # the unmatched elements. UNLESS they're whitespace and we should be greedy.
            if self.code_only:
                while True:
                    if len(unmatched_segments) == 0:
                        break
                    elif not unmatched_segments[0].is_code:
                        # We should add this one to the match and carry on
                        matched_segments += unmatched_segments[0],
                        unmatched_segments = unmatched_segments[1:]
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                        continue
                    else:
                        break

            return MatchResult(matched_segments.matched_segments, unmatched_segments)