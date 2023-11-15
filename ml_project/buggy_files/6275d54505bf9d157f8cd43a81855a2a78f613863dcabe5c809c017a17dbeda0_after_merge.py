    def _add_embeddings_to_sentences(self, sentences: List[Sentence]):
        """Match subtokenization to Flair tokenization and extract embeddings from transformers for each token."""

        # first, subtokenize each sentence and find out into how many subtokens each token was divided
        subtokenized_sentences = []
        subtokenized_sentences_token_lengths = []

        sentence_parts_lengths = []

        # TODO: keep for backwards compatibility, but remove in future
        # some pretrained models do not have this property, applying default settings now.
        # can be set manually after loading the model.
        if not hasattr(self, 'max_subtokens_sequence_length'):
            self.max_subtokens_sequence_length = None
            self.allow_long_sentences = False
            self.stride = 0

        non_empty_sentences = []
        empty_sentences = []

        for sentence in sentences:
            tokenized_string = sentence.to_tokenized_string()

            # method 1: subtokenize sentence
            # subtokenized_sentence = self.tokenizer.encode(tokenized_string, add_special_tokens=True)

            # method 2:
            # transformer specific tokenization
            subtokenized_sentence = self.tokenizer.tokenize(tokenized_string)
            if len(subtokenized_sentence) == 0:
                empty_sentences.append(sentence)
                continue
            else:
                non_empty_sentences.append(sentence)

            token_subtoken_lengths = self.reconstruct_tokens_from_subtokens(sentence, subtokenized_sentence)
            subtokenized_sentences_token_lengths.append(token_subtoken_lengths)

            subtoken_ids_sentence = self.tokenizer.convert_tokens_to_ids(subtokenized_sentence)

            nr_sentence_parts = 0

            while subtoken_ids_sentence:
                nr_sentence_parts += 1
                encoded_inputs = self.tokenizer.encode_plus(subtoken_ids_sentence,
                                                            max_length=self.max_subtokens_sequence_length,
                                                            stride=self.stride,
                                                            return_overflowing_tokens=self.allow_long_sentences,
                                                            truncation=True,
                                                            )

                subtoken_ids_split_sentence = encoded_inputs['input_ids']
                subtokenized_sentences.append(torch.tensor(subtoken_ids_split_sentence, dtype=torch.long))

                if 'overflowing_tokens' in encoded_inputs:
                    subtoken_ids_sentence = encoded_inputs['overflowing_tokens']
                else:
                    subtoken_ids_sentence = None

            sentence_parts_lengths.append(nr_sentence_parts)

        # empty sentences get zero embeddings
        for sentence in empty_sentences:
            for token in sentence:
                token.set_embedding(self.name, torch.zeros(self.embedding_length))

        # only embed non-empty sentences and if there is at least one
        sentences = non_empty_sentences
        if len(sentences) == 0: return

        # find longest sentence in batch
        longest_sequence_in_batch: int = len(max(subtokenized_sentences, key=len))

        total_sentence_parts = sum(sentence_parts_lengths)
        # initialize batch tensors and mask
        input_ids = torch.zeros(
            [total_sentence_parts, longest_sequence_in_batch],
            dtype=torch.long,
            device=flair.device,
        )
        mask = torch.zeros(
            [total_sentence_parts, longest_sequence_in_batch],
            dtype=torch.long,
            device=flair.device,
        )
        for s_id, sentence in enumerate(subtokenized_sentences):
            sequence_length = len(sentence)
            input_ids[s_id][:sequence_length] = sentence
            mask[s_id][:sequence_length] = torch.ones(sequence_length)
        
        # put encoded batch through transformer model to get all hidden states of all encoder layers
        if type(self.tokenizer) == TransfoXLTokenizer:
            hidden_states = self.model(input_ids)[-1]
        else:
            hidden_states = self.model(input_ids, attention_mask=mask)[-1]   # make the tuple a tensor; makes working with it easier.

        hidden_states = torch.stack(hidden_states)

        sentence_idx_offset = 0

        # gradients are enabled if fine-tuning is enabled
        gradient_context = torch.enable_grad() if (self.fine_tune and self.training) else torch.no_grad()

        with gradient_context:

            # iterate over all subtokenized sentences
            for sentence_idx, (sentence, subtoken_lengths, nr_sentence_parts) in enumerate(zip(sentences, subtokenized_sentences_token_lengths, sentence_parts_lengths)):

                sentence_hidden_state = hidden_states[:, sentence_idx + sentence_idx_offset, ...]

                for i in range(1, nr_sentence_parts):
                    sentence_idx_offset += 1
                    remainder_sentence_hidden_state = hidden_states[:, sentence_idx + sentence_idx_offset, ...]
                    # remove stride_size//2 at end of sentence_hidden_state, and half at beginning of remainder,
                    # in order to get some context into the embeddings of these words.
                    # also don't include the embedding of the extra [CLS] and [SEP] tokens.
                    sentence_hidden_state = torch.cat((sentence_hidden_state[:, :-1-self.stride//2, :],
                                                       remainder_sentence_hidden_state[:, 1 + self.stride//2:, :]), 1)

                subword_start_idx = self.begin_offset

                # for each token, get embedding
                for token_idx, (token, number_of_subtokens) in enumerate(zip(sentence, subtoken_lengths)):

                    # some tokens have no subtokens at all (if omitted by BERT tokenizer) so return zero vector
                    if number_of_subtokens == 0:
                        token.set_embedding(self.name, torch.zeros(self.embedding_length))
                        continue

                    subword_end_idx = subword_start_idx + number_of_subtokens

                    subtoken_embeddings: List[torch.FloatTensor] = []

                    # get states from all selected layers, aggregate with pooling operation
                    for layer in self.layer_indexes:
                        current_embeddings = sentence_hidden_state[layer][subword_start_idx:subword_end_idx]

                        if self.pooling_operation == "first":
                            final_embedding: torch.FloatTensor = current_embeddings[0]

                        if self.pooling_operation == "last":
                            final_embedding: torch.FloatTensor = current_embeddings[-1]

                        if self.pooling_operation == "first_last":
                            final_embedding: torch.Tensor = torch.cat([current_embeddings[0], current_embeddings[-1]])

                        if self.pooling_operation == "mean":
                            all_embeddings: List[torch.FloatTensor] = [
                                embedding.unsqueeze(0) for embedding in current_embeddings
                            ]
                            final_embedding: torch.Tensor = torch.mean(torch.cat(all_embeddings, dim=0), dim=0)

                        subtoken_embeddings.append(final_embedding)

                    # use scalar mix of embeddings if so selected
                    if self.use_scalar_mix:
                        sm_embeddings = torch.mean(torch.stack(subtoken_embeddings, dim=1), dim=1)
                        # sm_embeddings = self.mix(subtoken_embeddings)

                        subtoken_embeddings = [sm_embeddings]

                    # set the extracted embedding for the token
                    token.set_embedding(self.name, torch.cat(subtoken_embeddings))

                    subword_start_idx += number_of_subtokens