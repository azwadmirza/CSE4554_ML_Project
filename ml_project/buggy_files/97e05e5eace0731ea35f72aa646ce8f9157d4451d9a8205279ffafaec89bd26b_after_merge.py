    def set(self, key, value):
        self.connection.set(key, value, ttl=self.expires, format=FMT_AUTO)