    def get(self, key):
        current = msec_time()
        expired = [k for k, v in self._ttl.items() if current >= v]
        for expired_item_key in expired:
            self.delete(expired_item_key[len(self.prefix):])
        return self._store.get(self.prefix + key)