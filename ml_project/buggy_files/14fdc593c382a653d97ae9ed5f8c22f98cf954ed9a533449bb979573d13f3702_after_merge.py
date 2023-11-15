    def __getitem__(self, key):
        # matrix builder syntax, like 'a, b; c, d'
        if isinstance(key, str):
            raise MAError("Unavailable for masked array.")

        return super(MAxisConcatenator, self).__getitem__(key)