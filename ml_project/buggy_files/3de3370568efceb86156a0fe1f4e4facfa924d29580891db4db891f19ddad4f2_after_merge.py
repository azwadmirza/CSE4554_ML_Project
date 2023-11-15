    def _dict_to_samples(self, dictionary, all_dicts=None):
        assert len(all_dicts) > 1, "Need at least 2 documents to sample random sentences from"
        doc = dictionary["doc"]
        samples = []
        for idx in range(len(doc) - 1):
            text_a, text_b, is_next_label = get_sentence_pair(doc, all_dicts, idx)
            sample_in_clear_text = {
                "text_a": text_a,
                "text_b": text_b,
                "nextsentence_label": is_next_label,
            }
            tokenized = {}
            tokenized["text_a"] = tokenize_with_metadata(
                text_a, self.tokenizer, self.max_seq_len
            )
            tokenized["text_b"] = tokenize_with_metadata(
                text_b, self.tokenizer, self.max_seq_len
            )
            samples.append(
                Sample(id=None, clear_text=sample_in_clear_text, tokenized=tokenized)
            )
        return samples