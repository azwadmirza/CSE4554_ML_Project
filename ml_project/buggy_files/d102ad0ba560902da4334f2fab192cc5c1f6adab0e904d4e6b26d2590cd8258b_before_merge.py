    def insert(self, string):
        """Inserts ``string`` into the Trie

        :param string: String to insert into the trie
        :type string: str

        :Example:

        >>> from nltk.collections import Trie
        >>> trie = Trie(["ab"])
        >>> trie
        defaultdict(<class 'nltk.collections.Trie'>, {'a': defaultdict(<class 'nltk.collections.Trie'>, {'b': defaultdict(<class 'nltk.collections.Trie'>, {True: None})})})

        """
        if len(string):
            self[string[0]].insert(string[1:])
        else:
            # mark the string is complete
            self[Trie.LEAF] = None