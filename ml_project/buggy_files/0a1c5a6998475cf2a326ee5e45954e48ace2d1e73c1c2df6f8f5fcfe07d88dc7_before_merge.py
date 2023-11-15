    def ttl(self, key):
        ttl = self._ttl.get(self.prefix + key)
        if ttl is not None:
            return (ttl - utils.msec_time()) / 1000.0
        return -1