    def penn_tokenize(self, text, return_str=False):
        """
        This is a Python port of the Penn treebank tokenizer adapted by the Moses
        machine translation community. It's a little different from the
        version in nltk.tokenize.treebank.
        """
        # Converts input string into unicode.
        text = text_type(text)
        # Perform a chain of regex substituitions using MOSES_PENN_REGEXES_1
        for regexp, substitution in self.MOSES_PENN_REGEXES_1:
            text = re.sub(regexp, substitution, text)
        # Handles nonbreaking prefixes.
        text = self.handles_nonbreaking_prefixes(text)
        # Restore ellipsis, clean extra spaces, escape XML symbols.
        for regexp, substitution in self.MOSES_PENN_REGEXES_2:
            text = re.sub(regexp, substitution, text)
        return text if return_str else text.split()