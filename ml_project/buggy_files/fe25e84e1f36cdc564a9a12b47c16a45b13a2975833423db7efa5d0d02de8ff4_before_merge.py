    def _add_padding_to_batch(
        self, batch_token_ids: List[List[int]]
    ) -> Tuple[List[int], List[List[int]]]:
        """Add padding so that all examples in the batch are of the same length.

        Args:
            batch_token_ids: Batch of examples where each example is a non-padded list
            of token ids.

        Returns:
            Padded batch with all examples of the same length.
        """
        padded_token_ids = []
        # Compute max length across examples
        max_seq_len = 0
        actual_sequence_lengths = []

        for example_token_ids in batch_token_ids:
            actual_sequence_lengths.append(len(example_token_ids))
            max_seq_len = max(max_seq_len, len(example_token_ids))

        # Add padding according to max_seq_len
        # Some models don't contain pad token, we use unknown token as padding token.
        # This doesn't affect the computation since we compute an attention mask
        # anyways.
        for example_token_ids in batch_token_ids:
            padded_token_ids.append(
                example_token_ids
                + [self.pad_token_id] * (max_seq_len - len(example_token_ids))
            )
        return actual_sequence_lengths, padded_token_ids