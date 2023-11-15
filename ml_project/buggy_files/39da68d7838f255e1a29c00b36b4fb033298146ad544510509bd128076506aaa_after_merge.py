    def __missing__(self, key):
        self[key] = Trie()
        return self[key]