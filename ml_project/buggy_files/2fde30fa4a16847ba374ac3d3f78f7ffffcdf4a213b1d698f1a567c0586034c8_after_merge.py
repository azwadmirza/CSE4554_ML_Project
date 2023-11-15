    def tokenize(self, tokenizer):
        passage = (
            self.passage.lower()
            if model_resolution.resolve_is_lower_case(tokenizer=tokenizer)
            else self.passage
        )
        passage_tokens = tokenizer.tokenize(passage)
        token_aligner = TokenAligner(source=passage, target=passage_tokens)
        answer_token_span = token_aligner.project_char_to_token_span(
            self.answer_char_span[0], self.answer_char_span[1], inclusive=True
        )

        return TokenizedExample(
            guid=self.guid,
            passage=passage_tokens,
            question=tokenizer.tokenize(self.question),
            answer_str=self.answer,
            passage_str=passage,
            answer_token_span=answer_token_span,
            token_idx_to_char_idx_map=token_aligner.source_char_idx_to_target_token_idx.T,
        )