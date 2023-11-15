    def set(self, key, value, state):
        self.connection.set(key, value, ttl=self.expires, format=FMT_AUTO)