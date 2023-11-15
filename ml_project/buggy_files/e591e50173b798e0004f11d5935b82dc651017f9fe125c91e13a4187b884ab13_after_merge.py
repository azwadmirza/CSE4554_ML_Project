    def set(self, key, value):
        return self.client.set(key, value, self.expires)