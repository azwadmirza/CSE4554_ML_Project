    def _get_processed_message_tokens_by_attribute(
        self, message: "Message", attribute: Text = TEXT_ATTRIBUTE
    ) -> List[Text]:
        """Get processed text of attribute of a message"""

        if message.get(attribute) is None:
            # return empty string since sklearn countvectorizer does not like None
            # object while training and predicting
            return [""]

        tokens = self._get_message_tokens_by_attribute(message, attribute)
        tokens = self._process_tokens(tokens, attribute)
        tokens = self._replace_with_oov_token(tokens, attribute)

        return tokens