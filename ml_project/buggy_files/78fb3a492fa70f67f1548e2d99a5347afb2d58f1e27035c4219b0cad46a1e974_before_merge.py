    def _compute_attention_mask(actual_sequence_lengths: List[int]) -> np.ndarray:
        """Compute a mask for padding tokens.

        This mask will be used by the language model so that it does not attend to
        padding tokens.

        Args:
            actual_sequence_lengths: List of length of each example without any padding

        Returns:
            Computed attention mask, 0 for padding and 1 for non-padding tokens.
        """

        attention_mask = []
        max_seq_length = max(actual_sequence_lengths)
        for actual_sequence_length in actual_sequence_lengths:
            # add 1s for present tokens, fill up the remaining space up to max
            # sequence length with 0s (non-existing tokens)
            padded_sequence = [1] * actual_sequence_length + [0] * (
                max_seq_length - actual_sequence_length
            )
            attention_mask.append(padded_sequence)

        attention_mask = np.array(attention_mask).astype(np.float32)

        return attention_mask