    def __init__(self, relevant_ids, dictionary):
        """
        Args:
        ----
        relevant_ids: the set of words that occurrences should be accumulated for.
        dictionary: Dictionary instance with mappings for the relevant_ids.
        """
        super(WindowedTextsAnalyzer, self).__init__(relevant_ids, dictionary)
        self._none_token = self._vocab_size  # see _iter_texts for use of none token