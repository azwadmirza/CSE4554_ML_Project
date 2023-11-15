    def _set_spacy_features(self, message: Message, attribute: Text = TEXT):
        """Adds the spacy word vectors to the messages features."""

        message_attribute_doc = self.get_doc(message, attribute)

        if message_attribute_doc is not None:
            features = self._features_for_doc(message_attribute_doc)

            cls_token_vec = self._calculate_cls_vector(features, self.pooling_operation)
            features = np.concatenate([features, cls_token_vec])

            features = self._combine_with_existing_dense_features(
                message, features, DENSE_FEATURE_NAMES[attribute]
            )
            message.set(DENSE_FEATURE_NAMES[attribute], features)