    def _merge(self, matches):
        # get matches up to and including first important_match
        #   but if no important_match, then all matches are important_matches
        relevant_matches = self._first_important_matches(matches)

        # get individual lines from important_matches that were marked important
        # these will be prepended to the final result
        def get_marked_lines(match, marker, parameter_obj):
            return tuple(line
                         for line, flag in zip(match.value(parameter_obj),
                                               match.valueflags(parameter_obj))
                         if flag is marker) if match else ()
        top_lines = concat(get_marked_lines(m, ParameterFlag.top, self) for m in relevant_matches)

        # also get lines that were marked as bottom, but reverse the match order so that lines
        # coming earlier will ultimately be last
        bottom_lines = concat(get_marked_lines(m, ParameterFlag.bottom, self) for m in
                              reversed(relevant_matches))

        # now, concat all lines, while reversing the matches
        #   reverse because elements closer to the end of search path take precedence
        all_lines = concat(m.value(self) for m in reversed(relevant_matches))

        # stack top_lines + all_lines, then de-dupe
        top_deduped = tuple(unique(concatv(top_lines, all_lines)))

        # take the top-deduped lines, reverse them, and concat with reversed bottom_lines
        # this gives us the reverse of the order we want, but almost there
        # NOTE: for a line value marked both top and bottom, the bottom marker will win out
        #       for the top marker to win out, we'd need one additional de-dupe step
        bottom_deduped = unique(concatv(reversed(tuple(bottom_lines)), reversed(top_deduped)))
        # just reverse, and we're good to go
        return tuple(reversed(tuple(bottom_deduped)))