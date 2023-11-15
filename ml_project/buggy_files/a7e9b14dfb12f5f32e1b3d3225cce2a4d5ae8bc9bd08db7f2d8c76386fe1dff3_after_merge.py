    def _add_embeddings_internal(self, sentences: List[Sentence]) -> List[Sentence]:
        """Add embeddings to all words in a list of sentences. If embeddings are already added,
        updates only if embeddings are non-static."""

        # first, find longest sentence in batch
        longest_sentence_in_batch: int = len(
            max([self.tokenizer.tokenize(sentence.to_tokenized_string()) for sentence in sentences], key=len))

        # prepare id maps for BERT model
        features = self._convert_sentences_to_features(sentences, longest_sentence_in_batch)
        if torch.cuda.is_available():
            all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long).cuda()
            all_input_masks = torch.tensor([f.input_mask for f in features], dtype=torch.long).cuda()
        else:
            all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
            all_input_masks = torch.tensor([f.input_mask for f in features], dtype=torch.long)

        # put encoded batch through BERT model to get all hidden states of all encoder layers
        if torch.cuda.is_available():
            self.model.cuda()
        self.model.eval()
        all_encoder_layers, _ = self.model(all_input_ids, token_type_ids=None, attention_mask=all_input_masks)

        with torch.no_grad():

            for sentence_index, sentence in enumerate(sentences):

                feature = features[sentence_index]

                # get aggregated embeddings for each BERT-subtoken in sentence
                subtoken_embeddings = []
                for token_index, _ in enumerate(feature.tokens):
                    all_layers = []
                    for layer_index in self.layer_indexes:
                        layer_output = all_encoder_layers[int(layer_index)].detach().cpu()[sentence_index]
                        all_layers.append(layer_output[token_index])

                    subtoken_embeddings.append(torch.cat(all_layers))

                # get the current sentence object
                token_idx = 0
                for token in sentence:
                    # add concatenated embedding to sentence
                    token_idx += 1

                    if self.pooling_operation == 'first':
                        # use first subword embedding if pooling operation is 'first'
                        token.set_embedding(self.name, subtoken_embeddings[token_idx])
                    else:
                        # otherwise, do a mean over all subwords in token
                        embeddings = subtoken_embeddings[token_idx:token_idx + feature.token_subtoken_count[token.idx]]
                        embeddings = [embedding.unsqueeze(0) for embedding in embeddings]
                        mean = torch.mean(torch.cat(embeddings, dim=0), dim=0)
                        token.set_embedding(self.name, mean)

                    token_idx += feature.token_subtoken_count[token.idx] - 1

        return sentences