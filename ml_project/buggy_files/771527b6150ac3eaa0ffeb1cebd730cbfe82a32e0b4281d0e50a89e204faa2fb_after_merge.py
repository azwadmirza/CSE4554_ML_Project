    def _merge(self, matches):
        # get matches up to and including first important_match
        #   but if no important_match, then all matches are important_matches
        relevant_matches_and_values = tuple((match, match.value(self)) for match in
                                            self._first_important_matches(matches))
        for match, value in relevant_matches_and_values:
            if not isinstance(value, Mapping):
                raise InvalidTypeError(self.name, value, match.source, value.__class__.__name__,
                                       self._type.__name__)

        # mapkeys with important matches
        def key_is_important(match, key):
            return match.valueflags(self).get(key) is ParameterFlag.final
        important_maps = tuple(dict((k, v)
                                    for k, v in iteritems(match_value)
                                    if key_is_important(match, k))
                               for match, match_value in relevant_matches_and_values)
        # dump all matches in a dict
        # then overwrite with important matches
        return merge(concatv((v for _, v in relevant_matches_and_values),
                             reversed(important_maps)))