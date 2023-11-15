    def set(self, key, value, state):
        return self.client.set(key, value, self.expires)