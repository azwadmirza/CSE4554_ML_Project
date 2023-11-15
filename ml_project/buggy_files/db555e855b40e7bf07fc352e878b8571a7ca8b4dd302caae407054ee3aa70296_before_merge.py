    def match(self, segments, parse_context):
        """Match if this is a bracketed sequence, with content that matches one of the elements.

        1. work forwards to find the first bracket.
           If we find something other that whitespace, then fail out.
        2. Once we have the first bracket, we need to bracket count forward to find it's partner.
        3. Assuming we find it's partner then we try and match what goes between them.
           If we match, great. If not, then we return an empty match.
           If we never find it's partner then we return an empty match but should probably
           log a parsing warning, or error?

        """
        seg_buff = segments
        matched_segs = ()

        # Look for the first bracket
        start_match = self._code_only_sensitive_match(
            seg_buff, self.start_bracket,
            parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)
        if start_match:
            seg_buff = start_match.unmatched_segments
        else:
            # Can't find the opening bracket. No Match.
            return MatchResult.from_unmatched(segments)

        # Look for the closing bracket
        pre, end_match, _ = self._bracket_sensitive_look_ahead_match(
            segments=seg_buff, matchers=[self.end_bracket],
            parse_context=parse_context, code_only=self.code_only
        )
        if not end_match:
            raise SQLParseError(
                "Couldn't find closing bracket for opening bracket.",
                segment=matched_segs)

        # Match the content now we've confirmed the brackets. We use the
        # _longest helper function mostly just because it deals with multiple
        # matchers.
        content_match, _ = self._longest_code_only_sensitive_match(
            pre, self._elements,
            parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)

        # We require a complete match for the content (hopefully for obvious reasons)
        if content_match.is_complete():
            # We don't want to add metas if they're already there, so check
            if content_match.matched_segments and content_match.matched_segments[0].is_meta:
                pre_meta = ()
            else:
                pre_meta = (Indent(),)
            if end_match.matched_segments and end_match.matched_segments[0].is_meta:
                post_meta = ()
            else:
                post_meta = (Dedent(),)

            return MatchResult(
                start_match.matched_segments
                + pre_meta  # Add a meta indent here
                + content_match.matched_segments
                + post_meta  # Add a meta indent here
                + end_match.matched_segments,
                end_match.unmatched_segments)
        else:
            # Now if we've not matched there's a final option. If the content is optional
            # and we allow non-code, then if the content is all non-code then it could be
            # empty brackets and still match.
            # NB: We don't add indents here, because there's nothing to indent
            if (
                all(e.is_optional() for e in self._elements)
                and self.code_only
                and all(not e.is_code for e in pre)
            ):
                # It worked!
                return MatchResult(
                    start_match.matched_segments
                    + pre
                    + end_match.matched_segments,
                    end_match.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)