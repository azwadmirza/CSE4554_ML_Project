    def match(self, segments, parse_context):
        """Match a specific sequence of elements."""
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)

        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments

        for idx, elem in enumerate(self._elements):
            while True:
                # Is it an indent or dedent?
                if elem.is_meta:
                    # Work out how to find an appropriate pos_marker for
                    # the meta segment.
                    if matched_segments:
                        last_matched = matched_segments.matched_segments[-1]
                        meta_pos_marker = last_matched.get_end_pos_marker()
                    else:
                        meta_pos_marker = unmatched_segments[0].pos_marker
                    matched_segments += elem(pos_marker=meta_pos_marker)
                    break

                if len(unmatched_segments) == 0:
                    # We've run our of sequence without matching everyting.
                    # Do only optional elements remain.
                    if all(e.is_optional() for e in self._elements[idx:]):
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
                        matched_segments += (unmatched_segments[0],)
                        unmatched_segments = unmatched_segments[1:]
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                        continue

                    # It's not whitespace, so carry on to matching
                    elem_match = elem._match(
                        unmatched_segments, parse_context=parse_context.copy(incr='match_depth'))

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

        # If we get to here, we've matched all of the elements (or skipped them)
        # but still have some segments left (or perhaps have precisely zero left).
        # In either case, we're golden. Return successfully, with any leftovers as
        # the unmatched elements. UNLESS they're whitespace and we should be greedy.
        if self.code_only:
            while unmatched_segments and not unmatched_segments[0].is_code:
                # We should add this one to the match and carry on
                matched_segments += (unmatched_segments[0],)
                unmatched_segments = unmatched_segments[1:]
                check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)

        return MatchResult(matched_segments.matched_segments, unmatched_segments)