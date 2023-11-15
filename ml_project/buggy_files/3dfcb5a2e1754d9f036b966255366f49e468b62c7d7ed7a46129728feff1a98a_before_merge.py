    def _get_candidate_negatives(self):
        """Returns candidate negatives of size `self.negative` from the negative examples buffer.

        Returns
        -------
        numpy.array
            Array of shape (`self.negative`,) containing indices of negative nodes.

        """

        if self._negatives_buffer.num_items() < self.negative:
            # Note: np.random.choice much slower than random.sample for large populations, possible bottleneck
            uniform_numbers = self._np_random.random_sample(self._negatives_buffer_size)
            cumsum_table_indices = np.searchsorted(self._node_probabilities_cumsum, uniform_numbers)
            self._negatives_buffer = NegativesBuffer(cumsum_table_indices)
        return self._negatives_buffer.get_items(self.negative)