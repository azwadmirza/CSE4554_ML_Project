    def score_candidate(self, word_a, word_b, in_between):
        # Micro optimization: check for quick early-out conditions, before the actual scoring.
        word_a_cnt = self.vocab.get(word_a, 0)
        if word_a_cnt <= 0:
            return None, None

        word_b_cnt = self.vocab.get(word_b, 0)
        if word_b_cnt <= 0:
            return None, None

        phrase = self.delimiter.join([word_a] + in_between + [word_b])
        # XXX: Why do we care about *all* phrase tokens? Why not just score the start+end bigram?
        phrase_cnt = self.vocab.get(phrase, 0)
        if phrase_cnt <= 0:
            return None, None

        score = self.scoring(
            worda_count=word_a_cnt, wordb_count=word_b_cnt, bigram_count=phrase_cnt,
            len_vocab=len(self.vocab), min_count=self.min_count, corpus_word_count=self.corpus_word_count,
        )
        if score <= self.threshold:
            return None, None

        return phrase, score