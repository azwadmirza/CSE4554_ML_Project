    def _merge(self, matches):
        # get matches up to and including first important_match
        #   but if no important_match, then all matches are important_matches
        relevant_matches = self._first_important_matches(matches)

        # mapkeys with important matches
        def key_is_important(match, key):
            return match.valueflags(self).get(key) is ParameterFlag.final
        important_maps = tuple(dict((k, v)
                                    for k, v in iteritems(match.value(self))
                                    if key_is_important(match, k))
                               for match in relevant_matches)
        # dump all matches in a dict
        # then overwrite with important matches
        return merge(concatv((m.value(self) for m in relevant_matches),
                             reversed(important_maps)))