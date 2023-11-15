    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:

        duplicate_examples = set()
        for ex in training_data.intent_examples:
            if (
                ex.get(TEXT) in self.intent_keyword_map.keys()
                and ex.get(INTENT) != self.intent_keyword_map[ex.get(TEXT)]
            ):
                duplicate_examples.add(ex.get(TEXT))
                rasa.shared.utils.io.raise_warning(
                    f"Keyword '{ex.get(TEXT)}' is a keyword to trigger intent "
                    f"'{self.intent_keyword_map[ex.get(TEXT)]}' and also "
                    f"intent '{ex.get(INTENT)}', it will be removed "
                    f"from the list of keywords for both of them. "
                    f"Remove (one of) the duplicates from the training data.",
                    docs=DOCS_URL_COMPONENTS + "#keyword-intent-classifier",
                )
            else:
                self.intent_keyword_map[ex.get(TEXT)] = ex.get(INTENT)
        for keyword in duplicate_examples:
            self.intent_keyword_map.pop(keyword)
            logger.debug(
                f"Removed '{keyword}' from the list of keywords because it was "
                "a keyword for more than one intent."
            )

        self._validate_keyword_map()