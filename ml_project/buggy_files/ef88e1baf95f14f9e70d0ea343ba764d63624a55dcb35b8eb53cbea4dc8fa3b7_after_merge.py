    def match(self, segments, parse_context):
        # Type munging
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty()

        # Make some buffers
        seg_buff = segments
        matched_segments = MatchResult.from_empty()
        # delimiters is a list of tuples containing delimiter segments as we find them.
        delimiters = []

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            # Check to see whether we've exhausted the buffer (or it's all non-code)
            if len(seg_buff) == 0 or (self.code_only and all([not s.is_code for s in seg_buff])):
                # Append the remaining buffer in case we're in the not is_code case.
                matched_segments += seg_buff
                # Nothing left, this is potentially a trailling case?
                if self.allow_trailing and (self.min_delimiters is None or len(delimiters) >= self.min_delimiters):
                    # It is! (nothing left so no unmatched segments to append)
                    return matched_segments
                else:
                    MatchResult.from_unmatched(segments)

            # We rely on _bracket_sensitive_look_ahead_match to do the bracket counting
            # element of this now. We look ahead to find a delimiter or terminator.
            matchers = [self.delimiter]
            if self.terminator:
                matchers.append(self.terminator)
            pre, mat, m = self._bracket_sensitive_look_ahead_match(
                seg_buff, matchers, parse_context=parse_context.copy(incr='match_depth'),
                # NB: We don't want whitespace at this stage, that should default to
                # being passed to the elements in between.
                code_only=False)

            # Have we found a delimiter or terminator looking forward?
            if mat:
                if m is self.delimiter:
                    # Yes. Store it and then match the contents up to now.
                    delimiters.append(mat.matched_segments)
                # We now test the intervening section as to whether it matches one
                # of the things we're looking for. NB: If it's of zero length then
                # we return without trying it.
                if len(pre) > 0:
                    for elem in self._elements:
                        # We use the whitespace padded match to hoover up whitespace if enabled.
                        elem_match = self._code_only_sensitive_match(
                            pre, elem, parse_context=parse_context.copy(incr='match_depth'),
                            # This is where the configured code_only behaviour kicks in.
                            code_only=self.code_only)

                        if elem_match.is_complete():
                            # First add the segment up to the delimiter to the matched segments
                            matched_segments += elem_match
                            # Then it depends what we matched.
                            # Delimiter
                            if m is self.delimiter:
                                # Then add the delimiter to the matched segments
                                matched_segments += mat.matched_segments
                                # Break this for loop and move on, looking for the next delimiter
                                seg_buff = mat.unmatched_segments
                                # Still got some buffer left. Carry on.
                                break
                            # Terminator
                            elif m is self.terminator:
                                # We just return straight away here. We don't add the terminator to
                                # this match, it should go with the unmatched parts.

                                # First check we've had enough delimiters
                                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                                    return MatchResult.from_unmatched(segments)
                                else:
                                    return MatchResult(
                                        matched_segments.matched_segments,
                                        mat.all_segments())
                            else:
                                raise RuntimeError(
                                    ("I don't know how I got here. Matched instead on {0}, which "
                                     "doesn't appear to be delimiter or terminator").format(m))
                        else:
                            # We REQUIRE a complete match here between delimiters or up to a
                            # terminator. If it's only partial then we don't want it.
                            # NB: using the sensitive match above deals with whitespace
                            # appropriately.
                            continue
                    else:
                        # None of them matched, return unmatched.
                        return MatchResult.from_unmatched(segments)
                else:
                    # Zero length section between delimiters. Return unmatched.
                    return MatchResult.from_unmatched(segments)
            else:
                # No match for a delimiter looking forward, this means we're
                # at the end. In this case we look for a potential partial match
                # looking forward. We know it's a non-zero length section because
                # we checked that up front.

                # First check we're had enough delimiters, because if we haven't then
                # there's no sense to try matching
                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                    return MatchResult.from_unmatched(segments)

                # We use the whitespace padded match to hoover up whitespace if enabled,
                # and default to the longest matcher. We don't care which one matches.
                mat, _ = self._longest_code_only_sensitive_match(
                    seg_buff, self._elements, parse_context=parse_context.copy(incr='match_depth'),
                    code_only=self.code_only)
                if mat:
                    # We've got something at the end. Return!
                    return MatchResult(
                        matched_segments.matched_segments + mat.matched_segments,
                        mat.unmatched_segments
                    )
                else:
                    # No match at the end, are we allowed to trail? If we are then return,
                    # otherwise we fail because we can't match the last element.
                    if self.allow_trailing:
                        return MatchResult(matched_segments.matched_segments, seg_buff)
                    else:
                        return MatchResult.from_unmatched(segments)