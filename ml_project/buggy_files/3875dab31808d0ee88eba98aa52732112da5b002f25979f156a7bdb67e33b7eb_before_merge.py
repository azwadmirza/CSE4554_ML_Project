    def set(self, key, value, state):
        _key = self.bucket.new(key, data=value)
        _key.store()