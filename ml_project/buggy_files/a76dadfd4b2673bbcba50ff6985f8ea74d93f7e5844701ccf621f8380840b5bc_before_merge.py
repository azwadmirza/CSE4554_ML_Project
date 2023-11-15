    def set(self, key, value, state):
        with self.open(self._filename(key), 'wb') as outfile:
            outfile.write(ensure_bytes(value))