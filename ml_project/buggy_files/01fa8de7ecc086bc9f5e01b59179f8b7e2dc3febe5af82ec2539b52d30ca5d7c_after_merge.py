    def match(self, segments, parse_context):
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
                            forward_buffer, parse_context=parse_context.copy(incr='match_depth'))
                        if m:
                            matched_buffer += m.matched_segments
                            forward_buffer = m.unmatched_segments
                            break
                else:
                    # Unable to match the forward buffer. We must have found something
                    # which isn't on our element list. Crash out.
                    return MatchResult.from_unmatched(segments)