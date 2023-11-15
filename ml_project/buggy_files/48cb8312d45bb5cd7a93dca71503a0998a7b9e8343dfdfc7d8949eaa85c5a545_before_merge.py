    def get(self, key, default=None):

        if not self.has_key(key):
            return default
        try:
            val = self[key]
            return val
        except KeyError:
            return default