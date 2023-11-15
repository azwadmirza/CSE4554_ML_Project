    def __setitem__(self, item, value):
        with self.write_mutex:
            parent, key = self._require_parent(item)
            value = ensure_bytes(value)
            parent[key] = value