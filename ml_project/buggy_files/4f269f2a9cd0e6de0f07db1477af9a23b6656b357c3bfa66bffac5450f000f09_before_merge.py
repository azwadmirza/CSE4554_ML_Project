    def _features_for_patterns(
        self, message: Message, attribute: Text
    ) -> scipy.sparse.coo_matrix:
        """Checks which known patterns match the message.

        Given a sentence, returns a vector of {1,0} values indicating which
        regexes did match. Furthermore, if the
        message is tokenized, the function will mark all tokens with a dict
        relating the name of the regex to whether it was matched."""
        tokens = message.get(TOKENS_NAMES[attribute], [])
        seq_length = len(tokens)

        vec = np.zeros([seq_length, len(self.known_patterns)])

        for pattern_index, pattern in enumerate(self.known_patterns):
            matches = re.finditer(pattern["pattern"], message.text)
            matches = list(matches)

            for token_index, t in enumerate(tokens):
                patterns = t.get("pattern", default={})
                patterns[pattern["name"]] = False

                if t.text == CLS_TOKEN:
                    # make sure to set all patterns for the CLS token to False
                    # the attribute patterns is needed later on and in the tests
                    t.set("pattern", patterns)
                    continue

                for match in matches:
                    if t.start < match.end() and t.end > match.start():
                        patterns[pattern["name"]] = True
                        vec[token_index][pattern_index] = 1.0
                        if attribute in [RESPONSE_ATTRIBUTE, TEXT_ATTRIBUTE]:
                            # CLS token vector should contain all patterns
                            vec[-1][pattern_index] = 1.0

                t.set("pattern", patterns)

        return scipy.sparse.coo_matrix(vec)