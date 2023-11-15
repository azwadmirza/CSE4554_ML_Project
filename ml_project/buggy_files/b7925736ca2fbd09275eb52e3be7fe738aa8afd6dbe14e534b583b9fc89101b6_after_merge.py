    def _add_embeddings_to_sentence(self, sentence: Sentence):
        """Match subtokenization to Flair tokenization and extract embeddings from transformers for each token."""

        # TODO: keep for backwards compatibility, but remove in future
        # some pretrained models do not have this property, applying default settings now.
        # can be set manually after loading the model.
        if not hasattr(self, 'max_subtokens_sequence_length'):
            self.max_subtokens_sequence_length = None
            self.allow_long_sentences = False
            self.stride = 0

        # if we also use context, first expand sentence to include context
        if self.context_length > 0:

            # in case of contextualization, we must remember non-expanded sentence
            original_sentence = sentence

            # create expanded sentence and remember context offsets
            expanded_sentence, context_offset = self._expand_sentence_with_context(sentence)

            # overwrite sentence with expanded sentence
            sentence = expanded_sentence

        # subtokenize the sentence
        tokenized_string = sentence.to_tokenized_string()

        # method 1: subtokenize sentence
        # subtokenized_sentence = self.tokenizer.encode(tokenized_string, add_special_tokens=True)

        # method 2:
        # transformer specific tokenization
        subtokenized_sentence = self.tokenizer.tokenize(tokenized_string)

        # set zero embeddings for empty sentences and return
        if len(subtokenized_sentence) == 0:
            for token in sentence:
                token.set_embedding(self.name, torch.zeros(self.embedding_length))
            return

        # determine into how many subtokens each token is split
        token_subtoken_lengths = self.reconstruct_tokens_from_subtokens(sentence, subtokenized_sentence)

        # if sentence is too long, will be split into multiple parts
        sentence_splits = []

        # check if transformer version 3 is used - in this case use old handling
        import transformers
        if transformers.__version__.startswith('3'):

            # get sentence as list of subtoken ids
            subtoken_ids_sentence = self.tokenizer.convert_tokens_to_ids(subtokenized_sentence)

            while subtoken_ids_sentence:
                encoded_inputs = self.tokenizer.encode_plus(subtoken_ids_sentence,
                                                            max_length=self.max_subtokens_sequence_length,
                                                            stride=self.stride,
                                                            return_overflowing_tokens=self.allow_long_sentences,
                                                            truncation=True,
                                                            )

                sentence_splits.append(torch.tensor(encoded_inputs['input_ids'], dtype=torch.long))

                if 'overflowing_tokens' in encoded_inputs:
                    subtoken_ids_sentence = encoded_inputs['overflowing_tokens']
                else:
                    subtoken_ids_sentence = None

        # else if current transformer is used, use default handling
        else:
            encoded_inputs = self.tokenizer.encode_plus(tokenized_string,
                                                        max_length=self.max_subtokens_sequence_length,
                                                        stride=self.stride,
                                                        return_overflowing_tokens=self.allow_long_sentences,
                                                        truncation=True,
                                                        )

            # overlong sentences are handled as multiple splits
            for encoded_input in encoded_inputs['input_ids']:
                sentence_splits.append(torch.tensor(encoded_input, dtype=torch.long))

        # embed each sentence split
        hidden_states_of_all_splits = []
        for split_number, sentence_split in enumerate(sentence_splits):

            # initialize batch tensors and mask
            input_ids = sentence_split.unsqueeze(0).to(flair.device)

            # propagate gradients if fine-tuning and only during training
            propagate_gradients = self.fine_tune and self.training
            # increase memory effectiveness by skipping all but last sentence split
            if propagate_gradients and self.memory_effective_training and split_number < len(sentence_splits) - 1:
                propagate_gradients = False

            # put encoded batch through transformer model to get all hidden states of all encoder layers
            if propagate_gradients:
                hidden_states = self.model(input_ids)[-1]  # make the tuple a tensor; makes working with it easier.
            else:
                with torch.no_grad(): # deactivate gradients if not necessary
                    hidden_states = self.model(input_ids)[-1]

            # get hidden states as single tensor
            split_hidden_state = torch.stack(hidden_states)[:, 0, ...]
            hidden_states_of_all_splits.append(split_hidden_state)

        # put splits back together into one tensor using overlapping strides
        hidden_states = hidden_states_of_all_splits[0]
        for i in range(1, len(hidden_states_of_all_splits)):
            hidden_states = hidden_states[:, :-1 - self.stride // 2, :]
            next_split = hidden_states_of_all_splits[i]
            next_split = next_split[:, 1 + self.stride // 2:, :]
            hidden_states = torch.cat([hidden_states, next_split], 1)

        subword_start_idx = self.begin_offset

        # for each token, get embedding
        for token_idx, (token, number_of_subtokens) in enumerate(zip(sentence, token_subtoken_lengths)):

            # some tokens have no subtokens at all (if omitted by BERT tokenizer) so return zero vector
            if number_of_subtokens == 0:
                token.set_embedding(self.name, torch.zeros(self.embedding_length))
                continue

            subword_end_idx = subword_start_idx + number_of_subtokens

            subtoken_embeddings: List[torch.FloatTensor] = []

            # get states from all selected layers, aggregate with pooling operation
            for layer in self.layer_indexes:
                current_embeddings = hidden_states[layer][subword_start_idx:subword_end_idx]

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

            # use layer mean of embeddings if so selected
            if self.layer_mean and len(self.layer_indexes) > 1:
                sm_embeddings = torch.mean(torch.stack(subtoken_embeddings, dim=1), dim=1)
                subtoken_embeddings = [sm_embeddings]

            # set the extracted embedding for the token
            token.set_embedding(self.name, torch.cat(subtoken_embeddings))

            subword_start_idx += number_of_subtokens

        # move embeddings from context back to original sentence (if using context)
        if self.context_length > 0:
            for token_idx, token in enumerate(original_sentence):
                token.set_embedding(self.name, sentence[token_idx+context_offset].get_embedding(self.name))
            sentence = original_sentence