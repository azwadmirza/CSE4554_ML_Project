    def _expand_sentence_with_context(self, sentence):

        # remember original sentence
        original_sentence = sentence

        # get left context
        left_context = ''
        while True:
            sentence = sentence.previous_sentence()
            if sentence is None: break
            if self.respect_document_boundaries and sentence.is_document_boundary: break

            left_context = sentence.to_tokenized_string() + ' ' + left_context
            left_context = left_context.strip()
            if len(left_context.split(" ")) > self.context_length:
                left_context = " ".join(left_context.split(" ")[-self.context_length:])
                break
        context_length = len(left_context.split(" "))
        original_sentence.left_context = left_context

        # get right context
        sentence = original_sentence
        right_context = ''
        while True:
            sentence = sentence.next_sentence()
            if sentence is None: break
            if self.respect_document_boundaries and sentence.is_document_boundary: break

            right_context += ' ' + sentence.to_tokenized_string()
            right_context = right_context.strip()
            if len(right_context.split(" ")) > self.context_length:
                right_context = " ".join(right_context.split(" ")[:self.context_length])
                break
        original_sentence.right_context = right_context

        # make expanded sentence
        expanded_sentence = Sentence()
        expanded_sentence.tokens = [Token(token) for token in left_context.split(" ") +
                                    original_sentence.to_tokenized_string().split(" ") +
                                    right_context.split(" ")]
        return expanded_sentence, context_length