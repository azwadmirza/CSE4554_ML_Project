    def _tokenize_example(
        self, message: Message, attribute: Text
    ) -> Tuple[List[Token], List[int]]:

        tokens_in = self.whitespace_tokenizer.tokenize(message, attribute)

        tokens_out = []

        token_ids_out = []

        for token in tokens_in:
            # use lm specific tokenizer to further tokenize the text
            split_token_ids, split_token_strings = self._lm_tokenize(token.text)

            split_token_strings = self._lm_specific_token_cleanup(split_token_strings)

            token_ids_out += split_token_ids

            tokens_out += train_utils.align_tokens(
                split_token_strings, token.end, token.start
            )

        return tokens_out, token_ids_out