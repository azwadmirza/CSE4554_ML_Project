    def delete(self, key):
        del self._cache[key]
        self._db.delete(self._make_key(key))
        self._db.zrem(self._keys_set, key)