    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        """ The match function for `bracketed` implements bracket counting. """

        # 1. work forwards to find the first bracket.
        #    If we find something other that whitespace, then fail out.
        # 2. Once we have the first bracket, we need to bracket count forward to find it's partner.
        # 3. Assuming we find it's partner then we try and match what goes between them.
        #    If we match, great. If not, then we return an empty match.
        #    If we never find it's partner then we return an empty match but should probably
        #    log a parsing warning, or error?

        sub_bracket_count = 0
        pre_content_segments = tuple()
        unmatched_segs = segments
        matched_segs = tuple()
        current_bracket_segment = None

        # Step 1. Find the first useful segment
        # Work through to find the first code segment...
        if self.code_only:
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    break
                else:
                    matched_segs += seg,
                    unmatched_segs = unmatched_segs[1:]
            else:
                # We've trying to match on a sequence of segments which contain no code.
                # That means this isn't a match.
                return MatchResult.from_unmatched(segments)

        # is it a bracket?
        m = self.start_bracket._match(
            segments=unmatched_segs, match_depth=match_depth + 1,
            parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
            match_segment=match_segment)

        if m.has_match():
            # We've got the first bracket.
            # Update the seg_idx by the length of the match
            current_bracket_segment = m.matched_segments[0]
            # No indexing to allow mutation
            matched_segs += m.matched_segments
            unmatched_segs = m.unmatched_segments
        else:
            # Whatever we have, it doesn't start with a bracket.
            return MatchResult.from_unmatched(segments)

        # Step 2: Bracket count forward to find it's pair
        content_segments = tuple()
        pre_content_segments = matched_segs

        while True:
            # Are we at the end of the sequence?
            if len(unmatched_segs) == 0:
                # We've got to the end without finding the closing bracket
                # this isn't just parsing issue this is probably a syntax
                # error.
                # TODO: Format this better
                raise SQLParseError(
                    "Couldn't find closing bracket for opening bracket.",
                    segment=current_bracket_segment)

            # Is it a closing bracket?
            m = self.end_bracket._match(
                segments=unmatched_segs, match_depth=match_depth + 1,
                parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                match_segment=match_segment)
            if m.has_match():
                if sub_bracket_count == 0:
                    # We're back to the bracket pair!
                    matched_segs += m.matched_segments
                    unmatched_segs = m.unmatched_segments
                    closing_bracket_segs = m.matched_segments
                    break
                else:
                    # reduce the bracket count and then advance the counter.
                    sub_bracket_count -= 1
                    matched_segs += m.matched_segments
                    unmatched_segs = m.unmatched_segments
                    continue

            # Is it an opening bracket?
            m = self.start_bracket._match(
                segments=unmatched_segs, match_depth=match_depth + 1,
                parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                match_segment=match_segment)
            if m.has_match():
                # increment the open bracket counter and proceed
                sub_bracket_count += 1
                matched_segs += m.matched_segments
                unmatched_segs = m.unmatched_segments
                continue

            # If we get here it's not an opening bracket or a closing bracket
            # so we should carry on our merry way
            matched_segs += unmatched_segs[0],
            content_segments += unmatched_segs[0],
            unmatched_segs = unmatched_segs[1:]

        # If we get to here then we've found our closing bracket.
        # Let's identify the section to match for our content matchers
        # and then try it against each of them.

        for elem in self._elements:
            elem_match = elem._match(
                content_segments, match_depth=match_depth + 1,
                parse_depth=parse_depth, verbosity=verbosity, dialect=dialect,
                match_segment=match_segment)
            # Matches at this stage must be complete, because we've got nothing
            # to do with any leftovers within the brackets.
            if elem_match.is_complete():
                # We're also returning the *mutated* versions from the sub-matcher
                return MatchResult(
                    pre_content_segments
                    + elem_match.matched_segments
                    + closing_bracket_segs,
                    unmatched_segs)
            else:
                # Not matched this element, move on.
                # NB, a partial match here isn't helpful. We're matching
                # BETWEEN two delimiters and so it must be a complete match.
                # Incomplete matches are only possible at the end
                continue
        else:
            # If we're here we haven't matched any of the elements, then we have a problem
            return MatchResult.from_unmatched(segments)