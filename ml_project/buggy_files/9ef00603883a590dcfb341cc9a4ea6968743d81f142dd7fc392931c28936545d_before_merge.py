    def add_patterns(self, patterns):
        """Add patterns to the entitiy ruler. A pattern can either be a token
        pattern (list of dicts) or a phrase pattern (string). For example:
        {'label': 'ORG', 'pattern': 'Apple'}
        {'label': 'GPE', 'pattern': [{'lower': 'san'}, {'lower': 'francisco'}]}

        patterns (list): The patterns to add.

        DOCS: https://spacy.io/api/entityruler#add_patterns
        """

        # disable the nlp components after this one in case they hadn't been initialized / deserialised yet
        try:
            current_index = self.nlp.pipe_names.index(self.name)
            subsequent_pipes = [
                pipe for pipe in self.nlp.pipe_names[current_index + 1 :]
            ]
        except ValueError:
            subsequent_pipes = []
        with self.nlp.disable_pipes(subsequent_pipes):
            token_patterns = []
            phrase_pattern_labels = []
            phrase_pattern_texts = []
            phrase_pattern_ids = []

            for entry in patterns:
                if isinstance(entry["pattern"], basestring_):
                    phrase_pattern_labels.append(entry["label"])
                    phrase_pattern_texts.append(entry["pattern"])
                    phrase_pattern_ids.append(entry.get("id"))
                elif isinstance(entry["pattern"], list):
                    token_patterns.append(entry)

            phrase_patterns = []
            for label, pattern, ent_id in zip(
                phrase_pattern_labels,
                self.nlp.pipe(phrase_pattern_texts),
                phrase_pattern_ids,
            ):
                phrase_pattern = {"label": label, "pattern": pattern, "id": ent_id}
                if ent_id:
                    phrase_pattern["id"] = ent_id
                phrase_patterns.append(phrase_pattern)

            for entry in token_patterns + phrase_patterns:
                label = entry["label"]
                if "id" in entry:
                    ent_label = label
                    label = self._create_label(label, entry["id"])
                    key = self.matcher._normalize_key(label)
                    self._ent_ids[key] = (ent_label, entry["id"])

                pattern = entry["pattern"]
                if isinstance(pattern, Doc):
                    self.phrase_patterns[label].append(pattern)
                elif isinstance(pattern, list):
                    self.token_patterns[label].append(pattern)
                else:
                    raise ValueError(Errors.E097.format(pattern=pattern))
            for label, patterns in self.token_patterns.items():
                self.matcher.add(label, patterns)
            for label, patterns in self.phrase_patterns.items():
                self.phrase_matcher.add(label, patterns)