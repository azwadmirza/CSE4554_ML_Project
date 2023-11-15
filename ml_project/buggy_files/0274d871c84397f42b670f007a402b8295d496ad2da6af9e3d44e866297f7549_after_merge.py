    def __getitem__(self, key):
        try:
            return super(LocalWeakReferencedCache, self).__getitem__(key)
        except (TypeError, KeyError):
            return None  # key is either not weak-referenceable or not cached