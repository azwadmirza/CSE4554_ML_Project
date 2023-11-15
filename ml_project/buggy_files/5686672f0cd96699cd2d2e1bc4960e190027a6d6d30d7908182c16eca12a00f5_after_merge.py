    def expire(self, key, ttl):
        self._ttl[self.prefix + key] = msec_time() + int(ttl * 1000.0)