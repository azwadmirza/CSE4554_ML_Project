    def generate_new_attacked_text(self, new_words):
        """Returns a new AttackedText object and replaces old list of words
        with a new list of words, but preserves the punctuation and spacing of
        the original message.

        ``self.words`` is a list of the words in the current text with
        punctuation removed. However, each "word" in ``new_words`` could
        be an empty string, representing a word deletion, or a string
        with multiple space-separated words, representation an insertion
        of one or more words.
        """
        perturbed_text = ""
        original_text = AttackedText.SPLIT_TOKEN.join(self._text_input.values())
        new_attack_attrs = dict()
        if "label_names" in self.attack_attrs:
            new_attack_attrs["label_names"] = self.attack_attrs["label_names"]
        new_attack_attrs["newly_modified_indices"] = set()
        # Point to previously monitored text.
        new_attack_attrs["previous_attacked_text"] = self
        # Use `new_attack_attrs` to track indices with respect to the original
        # text.
        new_attack_attrs["modified_indices"] = self.attack_attrs[
            "modified_indices"
        ].copy()
        new_attack_attrs["original_index_map"] = self.attack_attrs[
            "original_index_map"
        ].copy()
        new_i = 0
        # Create the new attacked text by swapping out words from the original
        # text with a sequence of 0+ words in the new text.
        for i, (input_word, adv_word_seq) in enumerate(zip(self.words, new_words)):
            word_start = original_text.index(input_word)
            word_end = word_start + len(input_word)
            perturbed_text += original_text[:word_start]
            original_text = original_text[word_end:]
            adv_num_words = len(words_from_text(adv_word_seq))
            num_words_diff = adv_num_words - len(words_from_text(input_word))
            # Track indices on insertions and deletions.
            if num_words_diff != 0:
                # Re-calculated modified indices. If words are inserted or deleted,
                # they could change.
                shifted_modified_indices = set()
                for modified_idx in new_attack_attrs["modified_indices"]:
                    if modified_idx < i:
                        shifted_modified_indices.add(modified_idx)
                    elif modified_idx > i:
                        shifted_modified_indices.add(modified_idx + num_words_diff)
                    else:
                        pass
                new_attack_attrs["modified_indices"] = shifted_modified_indices
                # Track insertions and deletions wrt original text.
                # original_modification_idx = i
                new_idx_map = new_attack_attrs["original_index_map"].copy()
                if num_words_diff == -1:
                    new_idx_map[new_idx_map == i] = -1
                new_idx_map[new_idx_map > i] += num_words_diff
                new_attack_attrs["original_index_map"] = new_idx_map
            # Move pointer and save indices of new modified words.
            for j in range(i, i + adv_num_words):
                if input_word != adv_word_seq:
                    new_attack_attrs["modified_indices"].add(new_i)
                    new_attack_attrs["newly_modified_indices"].add(new_i)
                new_i += 1
            # Check spaces for deleted text.
            if adv_num_words == 0 and len(original_text):
                # Remove extra space (or else there would be two spaces for each
                # deleted word).
                # @TODO What to do with punctuation in this case? This behavior is undefined.
                if i == 0:
                    # If the first word was deleted, take a subsequent space.
                    if original_text[0] == " ":
                        original_text = original_text[1:]
                else:
                    # If a word other than the first was deleted, take a preceding space.
                    if perturbed_text[-1] == " ":
                        perturbed_text = perturbed_text[:-1]
            # Add substitute word(s) to new sentence.
            perturbed_text += adv_word_seq
        perturbed_text += original_text  # Add all of the ending punctuation.
        # Reform perturbed_text into an OrderedDict.
        perturbed_input_texts = perturbed_text.split(AttackedText.SPLIT_TOKEN)
        perturbed_input = OrderedDict(
            zip(self._text_input.keys(), perturbed_input_texts)
        )
        return AttackedText(perturbed_input, attack_attrs=new_attack_attrs)