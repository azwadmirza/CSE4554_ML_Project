    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        if isinstance(segments, BaseSegment):
            segments = [segments]
        seg_idx = 0
        terminal_idx = len(segments)
        sub_bracket_count = 0
        start_bracket_idx = None
        # delimiters is a list of tuples (idx, len), which keeps track of where
        # we found delimiters up to this point.
        delimiters = []
        matched_segments = MatchResult.from_empty()

        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty()

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            # Are we at the end of the sequence?
            if seg_idx >= terminal_idx:
                # Yes we're at the end

                # We now need to check whether everything from either the start
                # or from the last delimiter up to here matches. We CAN allow
                # a partial match at this stage.

                # Are we in a bracket counting cycle that hasn't finished yet?
                if sub_bracket_count > 0:
                    # TODO: Format this better
                    raise SQLParseError(
                        "Couldn't find closing bracket for opening bracket.",
                        segment=segments[start_bracket_idx])

                # Do we already have any delimiters?
                if delimiters:
                    # Yes, get the last delimiter
                    dm1 = delimiters[-1]
                    # get everything after the last delimiter
                    pre_segment = segments[dm1[0] + dm1[1]:terminal_idx]
                else:
                    # No, no delimiters at all so far.
                    # TODO: Allow this to be configured.
                    # Just get everything up to this point
                    pre_segment = segments[:terminal_idx]

                # Optionally here, we can match some non-code up front.
                if self.code_only:
                    while len(pre_segment) > 0:
                        if not pre_segment[0].is_code:
                            matched_segments += pre_segment[0],  # As tuple
                            pre_segment = pre_segment[1:]
                        else:
                            break

                # Check we actually have something left to match on
                if len(pre_segment) > 0:
                    # See if any of the elements match
                    for elem in self._elements:
                        elem_match = elem._match(
                            pre_segment, match_depth=match_depth + 1,
                            parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                            match_segment=match_segment)

                        if elem_match.has_match():
                            # Successfully matched one of the elements in this spot

                            # Add this match onto any already matched segments and return.
                            # We do this in a slightly odd way here to allow partial matches.

                            # we do a quick check on min_delimiters if present
                            if self.min_delimiters and len(delimiters) < self.min_delimiters:
                                # if we do have a limit and we haven't met it then crash out
                                return MatchResult.from_unmatched(segments)
                            return MatchResult(
                                matched_segments.matched_segments + elem_match.matched_segments,
                                elem_match.unmatched_segments + segments[terminal_idx:])
                        else:
                            # Not matched this element, move on.
                            # NB, a partial match here isn't helpful. We're matching
                            # BETWEEN two delimiters and so it must be a complete match.
                            # Incomplete matches are only possible at the end
                            continue

                # If we're here we haven't matched any of the elements on this last element.
                # BUT, if we allow trailing, and we have matched something, we can end on the last
                # delimiter
                if self.allow_trailing and len(matched_segments) > 0:
                    return MatchResult(matched_segments.matched_segments, pre_segment + segments[terminal_idx:])
                else:
                    return MatchResult.from_unmatched(segments)

            else:
                # We've got some sequence left.
                # Are we in a bracket cycle?
                if sub_bracket_count > 0:
                    # Is it another bracket entry?
                    bracket_match = self.start_bracket._match(
                        segments=segments[seg_idx:], match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                        match_segment=match_segment)
                    if bracket_match.has_match():
                        # increment the open bracket counter and proceed
                        sub_bracket_count += 1
                        seg_idx += len(bracket_match)
                        continue

                    # Is it a closing bracket?
                    bracket_match = self.end_bracket._match(
                        segments=segments[seg_idx:], match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                        match_segment=match_segment)
                    if bracket_match.has_match():
                        # reduce the bracket count and then advance the counter.
                        sub_bracket_count -= 1
                        seg_idx += len(bracket_match)
                        continue

                else:
                    # No bracket cycle
                    # Do we have a delimiter at the current index?

                    del_match = self.delimiter._match(
                        segments[seg_idx:], match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                        match_segment=match_segment)

                    # Doesn't have to match fully, just has to give us a delimiter.
                    if del_match.has_match():
                        # We've got at least a partial match
                        # Record the location of this delimiter
                        d = (seg_idx, len(del_match))
                        # Do we already have any delimiters?
                        if delimiters:
                            # Yes
                            dm1 = delimiters[-1]
                            # slice the segments between this delimiter and the previous
                            pre_segment = segments[dm1[0] + dm1[1]:d[0]]
                        else:
                            # No
                            # Just get everything up to this point
                            pre_segment = segments[:d[0]]
                        # Append the delimiter that we have found.
                        delimiters.append(d)

                        # Optionally here, we can match some non-code up front.
                        if self.code_only:
                            while len(pre_segment) > 0:
                                if not pre_segment[0].is_code:
                                    matched_segments += pre_segment[0],  # As tuple
                                    pre_segment = pre_segment[1:]
                                else:
                                    break

                        # We now check that this chunk matches whatever we're delimiting.
                        # In this case it MUST be a full match, not just a partial match
                        for elem in self._elements:
                            elem_match = elem._match(
                                pre_segment, match_depth=match_depth + 1,
                                parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                                match_segment=match_segment)

                            if elem_match.is_complete():
                                # Successfully matched one of the elements in this spot

                                # First add the segment up to the delimiter to the matched segments
                                matched_segments += elem_match
                                # Then add the delimiter to the matched segments
                                matched_segments += del_match
                                # Break this for loop and move on, looking for the next delimiter
                                seg_idx += len(del_match)
                                break
                            elif elem_match and self.code_only:
                                # Optionally if it's not a complete match but the unmatched bits are
                                # all non code then we'll also take it.
                                if all([not seg.is_code for seg in elem_match.unmatched_segments]):
                                    # Logic as above, just with the unmatched bits too because none are code
                                    matched_segments += elem_match.matched_segments
                                    matched_segments += elem_match.unmatched_segments
                                    matched_segments += del_match
                                    seg_idx += len(del_match)
                                    break
                                else:
                                    continue
                            else:
                                # Not matched this element, move on.
                                # NB, a partial match here isn't helpful. We're matching
                                # BETWEEN two delimiters and so it must be a complete match.
                                # Incomplete matches are only possible at the end
                                continue
                        else:
                            # If we're here we haven't matched any of the elements, then we have a problem
                            return MatchResult.from_unmatched(segments)
                    # This index doesn't have a delimiter, check for brackets and terminators

                    # First is it a terminator (and we're not in a bracket cycle)
                    if self.terminator:
                        term_match = self.terminator._match(
                            segments[seg_idx:], match_depth=match_depth + 1,
                            parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                            match_segment=match_segment)
                        if term_match:
                            # we've found a terminator.
                            # End the cycle here.
                            terminal_idx = seg_idx
                            continue

                    # Last, do we need to enter a bracket cycle
                    bracket_match = self.start_bracket._match(
                        segments=segments[seg_idx:], match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                        match_segment=match_segment)
                    if bracket_match.has_match():
                        # increment the open bracket counter and proceed
                        sub_bracket_count += 1
                        seg_idx += len(bracket_match)
                        continue

                # Nothing else interesting. Carry On
                # This is the same regardless of whether we're in the bracket cycle
                # or otherwise.
                seg_idx += 1