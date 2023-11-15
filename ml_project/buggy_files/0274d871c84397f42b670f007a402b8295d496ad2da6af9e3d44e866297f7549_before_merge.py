    def __getitem__(self, key):
        try:
            return super(LocalWeakReferencedCache, self).__getitem__(key)
        except TypeError:
            return None  # key is not weak-referenceable, it's not cached