    def add_mwe(self, mwe):
        """Add a multi-word expression to the lexicon (stored as a word trie)

        We use ``util.Trie`` to represent the trie. Its form is a dict of dicts. 
        The key True marks the end of a valid MWE.

        :param mwe: The multi-word expression we're adding into the word trie
        :type mwe: tuple(str) or list(str)

        :Example:

        >>> tokenizer = MWETokenizer()
        >>> tokenizer.add_mwe(('a', 'b'))
        >>> tokenizer.add_mwe(('a', 'b', 'c'))
        >>> tokenizer.add_mwe(('a', 'x'))
        >>> expected = {'a': {'x': {True: None}, 'b': {True: None, 'c': {True: None}}}}
        >>> tokenizer._mwes.as_dict() == expected
        True

        """
        self._mwes.insert(mwe)