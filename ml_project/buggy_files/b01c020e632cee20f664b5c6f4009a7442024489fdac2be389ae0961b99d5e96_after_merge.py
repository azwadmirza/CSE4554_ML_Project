    def getsize(self, path=None):
        path = normalize_storage_path(path)

        # obtain value to return size of
        value = None
        if path:
            try:
                parent, key = self._get_parent(path)
                value = parent[key]
            except KeyError:
                pass
        else:
            value = self.root

        # obtain size of value
        if value is None:
            return 0

        elif isinstance(value, self.cls):
            # total size for directory
            size = 0
            for v in value.values():
                if not isinstance(v, self.cls):
                    size += buffer_size(v)
            return size

        else:
            return buffer_size(value)