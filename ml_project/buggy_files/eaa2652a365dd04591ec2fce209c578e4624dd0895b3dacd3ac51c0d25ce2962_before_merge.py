    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0, dialect=None, match_segment=None):
        best_match = None
        # Match on each of the options
        for opt in self._elements:
            m = opt._match(segments, match_depth=match_depth + 1, parse_depth=parse_depth,
                           verbosity=verbosity, dialect=dialect, match_segment=match_segment)
            # If we get a complete match, just return it. If it's incomplete, then check to
            # see if it's all non-code if that allowed and match it
            if m.is_complete():
                # this will return on the *first* complete match
                return m
            elif m:
                if self.code_only:
                    # Attempt to consume whitespace if we can
                    matched_segments = m.matched_segments
                    unmatched_segments = m.unmatched_segments
                    while True:
                        if len(unmatched_segments) > 0:
                            if unmatched_segments[0].is_code:
                                break
                            else:
                                # Append as tuple
                                matched_segments += unmatched_segments[0],
                                unmatched_segments = unmatched_segments[1:]
                        else:
                            break
                    m = MatchResult(matched_segments, unmatched_segments)
                if best_match:
                    if len(m) > len(best_match):
                        best_match = m
                    else:
                        continue
                else:
                    best_match = m
                parse_match_logging(
                    parse_depth, match_depth, match_segment, self.__class__.__name__,
                    '_match', "Saving Match of Length {0}:  {1}".format(len(m), m),
                    verbosity=verbosity, v_level=self.v_level)
        else:
            # No full match from the first time round. If we've got a long partial match then return that.
            if best_match:
                return best_match
            # Ok so no match at all from the elements. Small getout if we can match any whitespace
            if self.code_only:
                matched_segs = tuple()
                unmatched_segs = segments
                # Look for non-code up front
                while True:
                    if len(unmatched_segs) == 0:
                        # We can't return a successful match on JUST whitespace
                        return MatchResult.from_unmatched(segments)
                    elif not unmatched_segs[0].is_code:
                        matched_segs += unmatched_segs[0],
                        unmatched_segs = unmatched_segs[1:]
                    else:
                        break
                # Now try and match
                for opt in self._elements:
                    m = opt._match(unmatched_segs, match_depth=match_depth + 1, parse_depth=parse_depth,
                                   verbosity=verbosity, dialect=dialect, match_segment=match_segment)
                    # Once again, if it's complete - return, if not wait to see if we get a more complete one
                    new_match = MatchResult(matched_segs + m.matched_segments, m.unmatched_segments)
                    if m.is_complete():
                        return new_match
                    elif m:
                        if best_match:
                            if len(best_match) > len(m):
                                best_match = m
                            else:
                                continue
                        else:
                            best_match = m
                        parse_match_logging(
                            parse_depth, match_depth, match_segment, self.__class__.__name__,
                            '_match', "Last-Ditch: Saving Match of Length {0}:  {1}".format(len(m), m),
                            verbosity=verbosity, v_level=self.v_level)
                else:
                    if best_match:
                        return MatchResult(matched_segs + best_match.matched_segments, best_match.unmatched_segments)
                    else:
                        return MatchResult.from_unmatched(segments)