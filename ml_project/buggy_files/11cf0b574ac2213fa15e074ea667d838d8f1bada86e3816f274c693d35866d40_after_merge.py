    def _learn_vocab(sentences, max_vocab_size, delimiter, connector_words, progress_per):
        """Collect unigram and bigram counts from the `sentences` iterable."""
        sentence_no, total_words, min_reduce = -1, 0, 1
        vocab = {}
        logger.info("collecting all words and their counts")
        for sentence_no, sentence in enumerate(sentences):
            if sentence_no % progress_per == 0:
                logger.info(
                    "PROGRESS: at sentence #%i, processed %i words and %i word types",
                    sentence_no, total_words, len(vocab),
                )
            start_token, in_between = None, []
            for word in sentence:
                if word not in connector_words:
                    vocab[word] = vocab.get(word, 0) + 1
                    if start_token is not None:
                        phrase_tokens = itertools.chain([start_token], in_between, [word])
                        joined_phrase_token = delimiter.join(phrase_tokens)
                        vocab[joined_phrase_token] = vocab.get(joined_phrase_token, 0) + 1
                    start_token, in_between = word, []  # treat word as both end of a phrase AND beginning of another
                elif start_token is not None:
                    in_between.append(word)
                total_words += 1

            if len(vocab) > max_vocab_size:
                utils.prune_vocab(vocab, min_reduce)
                min_reduce += 1

        logger.info(
            "collected %i token types (unigram + bigrams) from a corpus of %i words and %i sentences",
            len(vocab), total_words, sentence_no + 1,
        )
        return min_reduce, vocab, total_words