    def set(self, key, value):

        value2 = json.dumps(value)
        if self._timeout > 0:  # a timeout of 0 is handled as meaning 'never expire'
            self._db.setex(self._make_key(key), int(self._timeout), value2)
        else:
            self._db.set(self._make_key(key), value2)

        self._db.zadd(self._keys_set, time.time(), key)
        self._cache[key] = value