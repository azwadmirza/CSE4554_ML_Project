    def _intra_word_tokenize(
        self, string_tokens: List[str]
    ) -> Tuple[List[Token], List[Optional[Tuple[int, int]]]]:
        tokens: List[Token] = []
        offsets: List[Optional[Tuple[int, int]]] = []
        for token_string in string_tokens:
            wordpieces = self.tokenizer.encode_plus(
                token_string,
                add_special_tokens=False,
                return_tensors=None,
                return_offsets_mapping=False,
                return_attention_mask=False,
            )
            wp_ids = wordpieces["input_ids"]

            if len(wp_ids) > 0:
                offsets.append((len(tokens), len(tokens) + len(wp_ids) - 1))
                tokens.extend(
                    Token(text=wp_text, text_id=wp_id)
                    for wp_id, wp_text in zip(wp_ids, self.tokenizer.convert_ids_to_tokens(wp_ids))
                )
            else:
                offsets.append(None)
        return tokens, offsets