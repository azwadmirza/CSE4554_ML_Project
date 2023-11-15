    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        matched_buffer = tuple()
        forward_buffer = segments
        while True:
            if len(forward_buffer) == 0:
                # We're all good
                return MatchResult.from_matched(matched_buffer)
            elif self.code_only and not forward_buffer[0].is_code:
                matched_buffer += forward_buffer[0],
                forward_buffer = forward_buffer[1:]
            else:
                # Try and match it
                for opt in self._elements:
                    if isinstance(opt, str):
                        if forward_buffer[0].type == opt:
                            matched_buffer += forward_buffer[0],
                            forward_buffer = forward_buffer[1:]
                            break
                    else:
                        m = opt._match(
                            forward_buffer, match_depth=match_depth + 1, parse_depth=parse_depth,
                            verbosity=verbosity, dialect=dialect, match_segment=match_segment)
                        if m:
                            matched_buffer += m.matched_segments
                            forward_buffer = m.unmatched_segments
                            break
                else:
                    # Unable to match the forward buffer. We must have found something
                    # which isn't on our element list. Crash out.
                    return MatchResult.from_unmatched(segments)