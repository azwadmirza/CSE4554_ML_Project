    def __init__(self, strings=None):
        """Builds a Trie object, which is built around a ``defaultdict``

        If ``strings`` is provided, it will add the ``strings``, which
        consist of a ``list`` of ``strings``, to the Trie.
        Otherwise, it'll construct an empty Trie.

        :param strings: List of strings to insert into the trie
            (Default is ``None``)
        :type strings: list(str)

        """
        defaultdict.__init__(self, Trie)
        if strings:
            for string in strings:
                self.insert(string)