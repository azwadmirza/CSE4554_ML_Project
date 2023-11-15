    def _get_docs_for_batch(
        self, batch_examples: List[Message], attribute: Text
    ) -> List[Dict[Text, Any]]:
        """Compute language model docs for all examples in the batch.

        Args:
            batch_examples: Batch of message objects for which language model docs
            need to be computed.
            attribute: Property of message to be processed, one of ``TEXT`` or
            ``RESPONSE``.

        Returns:
            List of language model docs for each message in batch.
        """

        batch_tokens, batch_token_ids = self._get_token_ids_for_batch(
            batch_examples, attribute
        )

        (
            batch_sentence_features,
            batch_sequence_features,
        ) = self._get_model_features_for_batch(batch_token_ids, batch_tokens)

        # A doc consists of
        # {'token_ids': ..., 'tokens': ..., 'sequence_features': ...,
        # 'sentence_features': ...}
        batch_docs = []
        for index in range(len(batch_examples)):
            doc = {
                TOKEN_IDS: batch_token_ids[index],
                TOKENS: batch_tokens[index],
                SEQUENCE_FEATURES: batch_sequence_features[index],
                SENTENCE_FEATURES: np.reshape(batch_sentence_features[index], (1, -1)),
            }
            batch_docs.append(doc)

        return batch_docs