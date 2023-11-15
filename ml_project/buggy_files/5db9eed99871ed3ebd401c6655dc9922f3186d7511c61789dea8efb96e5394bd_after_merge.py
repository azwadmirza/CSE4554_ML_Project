    def predict(self, sentences: Union[List[Sentence], Sentence], mini_batch_size=32) -> List[Sentence]:

        if type(sentences) is Sentence:
            sentences = [sentences]

        # remove previous embeddings
        clear_embeddings(sentences)

        # make mini-batches
        batches = [sentences[x:x + mini_batch_size] for x in range(0, len(sentences), mini_batch_size)]

        for batch in batches:
            score, tag_seq = self._predict_scores_batch(batch)
            predicted_id = tag_seq
            all_tokens = []
            for sentence in batch:
                all_tokens.extend(sentence.tokens)

            for (token, pred_id) in zip(all_tokens, predicted_id):
                token: Token = token
                # get the predicted tag
                predicted_tag = self.tag_dictionary.get_item_for_index(pred_id)
                token.add_tag(self.tag_type, predicted_tag)

        return sentences