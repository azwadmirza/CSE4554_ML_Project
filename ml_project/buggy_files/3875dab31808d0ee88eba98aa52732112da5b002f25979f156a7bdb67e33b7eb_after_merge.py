    def set(self, key, value):
        _key = self.bucket.new(key, data=value)
        _key.store()