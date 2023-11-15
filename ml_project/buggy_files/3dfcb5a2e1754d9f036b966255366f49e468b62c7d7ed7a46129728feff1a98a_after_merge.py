    def _get_candidate_negatives(self):
        """Returns candidate negatives of size `self.negative` from the negative examples buffer.

        Returns
        -------
        numpy.array
            Array of shape (`self.negative`,) containing indices of negative nodes.

        """

        if self._negatives_buffer.num_items() < self.negative:
            # cumsum table of counts used instead of the standard approach of a probability cumsum table
            # this is to avoid floating point errors that result when the number of nodes is very high
            # for reference: https://github.com/RaRe-Technologies/gensim/issues/1917
            max_cumsum_value = self._node_counts_cumsum[-1]
            uniform_numbers = self._np_random.randint(1, max_cumsum_value + 1, self._negatives_buffer_size)
            cumsum_table_indices = np.searchsorted(self._node_counts_cumsum, uniform_numbers)
            self._negatives_buffer = NegativesBuffer(cumsum_table_indices)
        return self._negatives_buffer.get_items(self.negative)