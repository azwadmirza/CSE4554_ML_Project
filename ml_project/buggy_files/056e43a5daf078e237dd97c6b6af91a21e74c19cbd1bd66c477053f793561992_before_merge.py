    def __call__(self, string, univ_pos, morphology=None):
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        if "lemma_rules" not in self.lookups:
            return [lookup_table.get(string, string)]
        if univ_pos in (NOUN, "NOUN", "noun"):
            univ_pos = "noun"
        elif univ_pos in (VERB, "VERB", "verb"):
            univ_pos = "verb"
        elif univ_pos in (ADJ, "ADJ", "adj"):
            univ_pos = "adj"
        elif univ_pos in (ADP, "ADP", "adp"):
            univ_pos = "adp"
        elif univ_pos in (ADV, "ADV", "adv"):
            univ_pos = "adv"
        elif univ_pos in (AUX, "AUX", "aux"):
            univ_pos = "aux"
        elif univ_pos in (CCONJ, "CCONJ", "cconj"):
            univ_pos = "cconj"
        elif univ_pos in (DET, "DET", "det"):
            univ_pos = "det"
        elif univ_pos in (PRON, "PRON", "pron"):
            univ_pos = "pron"
        elif univ_pos in (PUNCT, "PUNCT", "punct"):
            univ_pos = "punct"
        elif univ_pos in (SCONJ, "SCONJ", "sconj"):
            univ_pos = "sconj"
        else:
            return [self.lookup(string)]
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(univ_pos, morphology):
            return list(set([string.lower()]))
        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(univ_pos, []),
        )
        return lemmas